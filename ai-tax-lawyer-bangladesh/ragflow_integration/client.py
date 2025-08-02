"""
RAGFlow API client for AI Tax Lawyer Bangladesh.
Handles communication with RAGFlow instance for knowledge retrieval.
"""
import httpx
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import hashlib
from pathlib import Path

from config.settings import settings, RAGFlowConfig
from utils.logging_utils import log_ragflow_operation, ContextualLogger

logger = ContextualLogger("ragflow.client")

class RAGFlowClient:
    """Async client for RAGFlow API operations."""
    
    def __init__(
        self,
        api_url: str = None,
        api_key: str = None,
        timeout: int = 30
    ):
        self.api_url = api_url or settings.ragflow_api_url
        self.api_key = api_key or settings.ragflow_api_key
        self.timeout = timeout
        self.knowledge_base = settings.ragflow_knowledge_base
        
        # HTTP client with proper configuration
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=timeout
        )
        
        # Collection configurations
        self.collection_configs = RAGFlowConfig.COLLECTIONS
        
        logger.add_context(knowledge_base=self.knowledge_base)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def health_check(self) -> bool:
        """Check if RAGFlow instance is healthy."""
        try:
            start_time = datetime.utcnow()
            response = await self.client.get("/health")
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if response.status_code == 200:
                log_ragflow_operation("health_check", "system", "", 1, duration_ms, True)
                logger.info("RAGFlow health check passed")
                return True
            else:
                log_ragflow_operation("health_check", "system", "", 0, duration_ms, False, 
                                    f"Status: {response.status_code}")
                logger.error(f"RAGFlow health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"RAGFlow health check error: {e}")
            return False
    
    async def create_knowledge_base(self, name: str, description: str = "") -> bool:
        """Create a new knowledge base."""
        try:
            start_time = datetime.utcnow()
            
            payload = {
                "name": name,
                "description": description,
                "language": "en",
                "permission": "me",
                "chunk_method": "naive",
                "parser_config": {
                    "chunk_token_count": 1024,
                    "layout_recognize": True,
                    "task_page_size": 12
                }
            }
            
            response = await self.client.post("/knowledge_bases", json=payload)
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if response.status_code in [200, 201]:
                log_ragflow_operation("create_kb", name, "", 1, duration_ms, True)
                logger.info(f"Created knowledge base: {name}")
                return True
            else:
                error_msg = f"Status: {response.status_code}, Body: {response.text}"
                log_ragflow_operation("create_kb", name, "", 0, duration_ms, False, error_msg)
                logger.error(f"Failed to create knowledge base {name}: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating knowledge base {name}: {e}")
            return False
    
    async def create_collection(
        self,
        collection_name: str,
        description: str = "",
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> bool:
        """Create a document collection within the knowledge base."""
        try:
            start_time = datetime.utcnow()
            
            payload = {
                "name": collection_name,
                "description": description,
                "language": "en",
                "embedding_model": settings.openai_embedding_model,
                "chunk_method": "naive",
                "parser_config": {
                    "chunk_token_count": chunk_size,
                    "chunk_overlap": overlap,
                    "layout_recognize": True,
                    "task_page_size": 12
                }
            }
            
            response = await self.client.post(
                f"/knowledge_bases/{self.knowledge_base}/datasets",
                json=payload
            )
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if response.status_code in [200, 201]:
                log_ragflow_operation("create_collection", collection_name, "", 1, duration_ms, True)
                logger.info(f"Created collection: {collection_name}")
                return True
            else:
                error_msg = f"Status: {response.status_code}, Body: {response.text}"
                log_ragflow_operation("create_collection", collection_name, "", 0, duration_ms, False, error_msg)
                logger.error(f"Failed to create collection {collection_name}: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            return False
    
    async def upload_document(
        self,
        collection_name: str,
        document_content: str,
        document_name: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Upload a document to a collection."""
        try:
            start_time = datetime.utcnow()
            
            # Create temporary file for upload
            temp_file = Path(f"/tmp/{document_name}.txt")
            temp_file.write_text(document_content, encoding='utf-8')
            
            files = {
                "file": (document_name, temp_file.open('rb'), "text/plain")
            }
            
            data = {
                "name": document_name,
                "metadata": json.dumps(metadata or {})
            }
            
            response = await self.client.post(
                f"/knowledge_bases/{self.knowledge_base}/datasets/{collection_name}/documents",
                files=files,
                data=data
            )
            
            # Cleanup
            temp_file.unlink(missing_ok=True)
            
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if response.status_code in [200, 201]:
                log_ragflow_operation("upload_document", collection_name, document_name, 1, duration_ms, True)
                logger.info(f"Uploaded document: {document_name} to {collection_name}")
                return True
            else:
                error_msg = f"Status: {response.status_code}, Body: {response.text}"
                log_ragflow_operation("upload_document", collection_name, document_name, 0, duration_ms, False, error_msg)
                logger.error(f"Failed to upload document {document_name}: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading document {document_name}: {e}")
            return False
    
    async def search(
        self,
        query: str,
        collection: str = None,
        top_k: int = 5,
        filters: Dict[str, Any] = None,
        retrieval_strategy: str = "hybrid_search"
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents in collections."""
        try:
            start_time = datetime.utcnow()
            
            # Prepare search payload
            payload = {
                "question": query,
                "conversation_id": self._generate_conversation_id(query),
                "datasets": [collection] if collection else list(self.collection_configs.keys()),
                "document_ids": [],
                "top_k": top_k,
                "similarity_threshold": filters.get("relevance_threshold", 0.7) if filters else 0.7,
                "vector_similarity_weight": 0.3,
                "rerank_id": "",
                "keyword_similarity_weight": 0.7
            }
            
            # Apply retrieval strategy
            if retrieval_strategy == "semantic_search":
                payload["vector_similarity_weight"] = 0.8
                payload["keyword_similarity_weight"] = 0.2
            elif retrieval_strategy == "keyword_semantic_hybrid":
                payload["vector_similarity_weight"] = 0.5
                payload["keyword_similarity_weight"] = 0.5
            elif retrieval_strategy == "exact_match_semantic":
                payload["vector_similarity_weight"] = 0.2
                payload["keyword_similarity_weight"] = 0.8
            
            response = await self.client.post(
                f"/knowledge_bases/{self.knowledge_base}/retrieval",
                json=payload
            )
            
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if response.status_code == 200:
                results = response.json()
                chunks = results.get("chunks", [])
                
                # Process and format results
                formatted_results = self._format_search_results(chunks)
                
                log_ragflow_operation("search", collection or "all", query, len(formatted_results), duration_ms, True)
                logger.info(f"Search completed: {len(formatted_results)} results for '{query[:50]}...'")
                
                return formatted_results
            else:
                error_msg = f"Status: {response.status_code}, Body: {response.text}"
                log_ragflow_operation("search", collection or "all", query, 0, duration_ms, False, error_msg)
                logger.error(f"Search failed: {error_msg}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    async def get_document_chunks(
        self,
        document_id: str,
        collection: str
    ) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document."""
        try:
            start_time = datetime.utcnow()
            
            response = await self.client.get(
                f"/knowledge_bases/{self.knowledge_base}/datasets/{collection}/documents/{document_id}/chunks"
            )
            
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if response.status_code == 200:
                chunks = response.json().get("chunks", [])
                log_ragflow_operation("get_chunks", collection, document_id, len(chunks), duration_ms, True)
                return chunks
            else:
                error_msg = f"Status: {response.status_code}"
                log_ragflow_operation("get_chunks", collection, document_id, 0, duration_ms, False, error_msg)
                return []
                
        except Exception as e:
            logger.error(f"Error getting document chunks: {e}")
            return []
    
    async def delete_document(
        self,
        document_id: str,
        collection: str
    ) -> bool:
        """Delete a document from a collection."""
        try:
            start_time = datetime.utcnow()
            
            response = await self.client.delete(
                f"/knowledge_bases/{self.knowledge_base}/datasets/{collection}/documents/{document_id}"
            )
            
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if response.status_code in [200, 204]:
                log_ragflow_operation("delete_document", collection, document_id, 1, duration_ms, True)
                logger.info(f"Deleted document: {document_id}")
                return True
            else:
                error_msg = f"Status: {response.status_code}"
                log_ragflow_operation("delete_document", collection, document_id, 0, duration_ms, False, error_msg)
                return False
                
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections in the knowledge base."""
        try:
            start_time = datetime.utcnow()
            
            response = await self.client.get(f"/knowledge_bases/{self.knowledge_base}/datasets")
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if response.status_code == 200:
                collections = response.json().get("datasets", [])
                log_ragflow_operation("list_collections", "system", "", len(collections), duration_ms, True)
                return collections
            else:
                log_ragflow_operation("list_collections", "system", "", 0, duration_ms, False)
                return []
                
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    async def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get statistics for a collection."""
        try:
            start_time = datetime.utcnow()
            
            response = await self.client.get(
                f"/knowledge_bases/{self.knowledge_base}/datasets/{collection}/stats"
            )
            
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if response.status_code == 200:
                stats = response.json()
                log_ragflow_operation("get_stats", collection, "", 1, duration_ms, True)
                return stats
            else:
                log_ragflow_operation("get_stats", collection, "", 0, duration_ms, False)
                return {}
                
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def _generate_conversation_id(self, query: str) -> str:
        """Generate a conversation ID for the query."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        return f"conv_{timestamp}_{query_hash}"
    
    def _format_search_results(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format search results into a standardized structure."""
        formatted_results = []
        
        for chunk in chunks:
            result = {
                "chunk_id": chunk.get("id", ""),
                "document_id": chunk.get("document_id", ""),
                "document_name": chunk.get("document_name", ""),
                "content": chunk.get("content_with_weight", chunk.get("content", "")),
                "score": chunk.get("similarity", 0.0),
                "metadata": {
                    "page_number": chunk.get("page_number"),
                    "chunk_index": chunk.get("positions", [{}])[0].get("page_number", 0),
                    "document_type": chunk.get("document_type"),
                    "keywords": chunk.get("keywords", [])
                },
                "source": {
                    "collection": chunk.get("kb_name", ""),
                    "retrieval_method": "ragflow_search"
                }
            }
            formatted_results.append(result)
        
        # Sort by relevance score
        formatted_results.sort(key=lambda x: x["score"], reverse=True)
        
        return formatted_results

class RAGFlowManager:
    """High-level manager for RAGFlow operations."""
    
    def __init__(self, client: RAGFlowClient = None):
        self.client = client or RAGFlowClient()
        self.collection_configs = RAGFlowConfig.COLLECTIONS
        self.logger = ContextualLogger("ragflow.manager")
    
    async def setup_knowledge_base(self) -> bool:
        """Setup the complete knowledge base with all collections."""
        try:
            self.logger.info("Setting up RAGFlow knowledge base...")
            
            # Check health first
            if not await self.client.health_check():
                self.logger.error("RAGFlow instance is not healthy")
                return False
            
            # Create knowledge base
            kb_created = await self.client.create_knowledge_base(
                name=settings.ragflow_knowledge_base,
                description="Bangladesh Tax Law Knowledge Base for AI Tax Lawyer"
            )
            
            if not kb_created:
                self.logger.warning("Knowledge base creation failed or already exists")
            
            # Create all collections
            success_count = 0
            for collection_name, config in self.collection_configs.items():
                success = await self.client.create_collection(
                    collection_name=collection_name,
                    description=f"Collection for {collection_name.replace('_', ' ')}",
                    chunk_size=config["chunk_size"],
                    overlap=config["overlap"]
                )
                
                if success:
                    success_count += 1
                    self.logger.info(f"✅ Created collection: {collection_name}")
                else:
                    self.logger.error(f"❌ Failed to create collection: {collection_name}")
            
            self.logger.info(f"Created {success_count}/{len(self.collection_configs)} collections")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error setting up knowledge base: {e}")
            return False
    
    async def batch_upload_documents(
        self,
        documents: List[Dict[str, Any]],
        collection_mapping: Dict[str, str] = None
    ) -> bool:
        """Upload multiple documents with proper collection mapping."""
        try:
            self.logger.info(f"Starting batch upload of {len(documents)} documents...")
            
            upload_count = 0
            for doc in documents:
                # Determine target collection
                target_collection = self._determine_target_collection(doc, collection_mapping)
                
                if not target_collection:
                    self.logger.warning(f"No target collection for document: {doc.get('title', 'Unknown')}")
                    continue
                
                # Upload document
                success = await self.client.upload_document(
                    collection_name=target_collection,
                    document_content=doc.get("content", ""),
                    document_name=doc.get("title", f"doc_{doc.get('document_id', 'unknown')}"),
                    metadata={
                        "document_id": doc.get("document_id"),
                        "document_type": doc.get("document_type"),
                        "year": doc.get("year"),
                        "language": doc.get("language"),
                        "source": doc.get("source", {})
                    }
                )
                
                if success:
                    upload_count += 1
                    
                if upload_count % 10 == 0:
                    self.logger.info(f"Uploaded {upload_count}/{len(documents)} documents")
            
            self.logger.info(f"✅ Uploaded {upload_count} documents successfully")
            return upload_count > 0
            
        except Exception as e:
            self.logger.error(f"Error in batch upload: {e}")
            return False
    
    def _determine_target_collection(
        self,
        document: Dict[str, Any],
        collection_mapping: Dict[str, str] = None
    ) -> Optional[str]:
        """Determine which collection a document should be uploaded to."""
        doc_type = document.get("document_type", "")
        
        # Use explicit mapping if provided
        if collection_mapping and doc_type in collection_mapping:
            return collection_mapping[doc_type]
        
        # Default mapping based on document type
        type_to_collection = {
            "income_tax_act": "income_tax_collection",
            "corporate_tax_provision": "corporate_tax_collection",
            "vat_act": "vat_customs_collection",
            "customs_act": "vat_customs_collection",
            "tds_circular": "tds_collection",
            "sro": "vat_customs_collection",
            "legal_precedent": "legal_precedents_collection",
            "form_template": "forms_procedures_collection",
            "guideline": "forms_procedures_collection",
            "amendment": "income_tax_collection"
        }
        
        return type_to_collection.get(doc_type, "forms_procedures_collection")

# Convenience functions for common operations

async def setup_ragflow_knowledge_base() -> bool:
    """Setup the complete RAGFlow knowledge base."""
    async with RAGFlowClient() as client:
        manager = RAGFlowManager(client)
        return await manager.setup_knowledge_base()

async def search_legal_knowledge(
    query: str,
    collection: str = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """Search for legal knowledge across collections."""
    async with RAGFlowClient() as client:
        return await client.search(query, collection, top_k)

async def upload_legal_documents(
    documents: List[Dict[str, Any]]
) -> bool:
    """Upload legal documents to appropriate collections."""
    async with RAGFlowClient() as client:
        manager = RAGFlowManager(client)
        return await manager.batch_upload_documents(documents)