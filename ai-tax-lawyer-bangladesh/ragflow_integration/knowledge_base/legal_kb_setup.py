#!/usr/bin/env python3
"""
RAGFlow Knowledge Base setup script for Bangladesh Tax Law.
Creates collections and uploads legal documents.
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from motor.motor_asyncio import AsyncIOMotorClient
from ragflow_integration.client import RAGFlowClient, RAGFlowManager
from config.settings import settings
from utils.logging_utils import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class LegalKnowledgeBaseSetup:
    """Handles complete setup of legal knowledge base in RAGFlow."""
    
    def __init__(self):
        self.ragflow_client = RAGFlowClient()
        self.ragflow_manager = RAGFlowManager(self.ragflow_client)
        self.mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
        self.mongodb_db = self.mongodb_client[settings.mongodb_database]
    
    async def setup_complete_knowledge_base(self) -> bool:
        """Setup the complete legal knowledge base."""
        try:
            logger.info("🚀 Starting complete legal knowledge base setup...")
            
            # Step 1: Setup RAGFlow knowledge base and collections
            step1_success = await self.setup_ragflow_structure()
            
            if not step1_success:
                logger.error("Failed to setup RAGFlow structure")
                return False
            
            # Step 2: Migrate documents from MongoDB to RAGFlow
            step2_success = await self.migrate_documents_to_ragflow()
            
            if not step2_success:
                logger.error("Failed to migrate documents to RAGFlow")
                return False
            
            # Step 3: Validate setup
            step3_success = await self.validate_knowledge_base()
            
            if step3_success:
                logger.info("✅ Legal knowledge base setup completed successfully!")
                return True
            else:
                logger.warning("⚠️  Knowledge base setup completed with some issues")
                return False
                
        except Exception as e:
            logger.error(f"❌ Knowledge base setup failed: {e}")
            return False
        finally:
            await self.cleanup()
    
    async def setup_ragflow_structure(self) -> bool:
        """Setup RAGFlow knowledge base structure."""
        try:
            logger.info("Setting up RAGFlow knowledge base structure...")
            
            # Check RAGFlow health
            if not await self.ragflow_client.health_check():
                logger.error("RAGFlow instance is not accessible")
                return False
            
            # Setup knowledge base and collections
            setup_success = await self.ragflow_manager.setup_knowledge_base()
            
            if setup_success:
                logger.info("✅ RAGFlow structure setup completed")
                
                # List created collections for verification
                collections = await self.ragflow_client.list_collections()
                logger.info(f"Created collections: {[c.get('name', 'Unknown') for c in collections]}")
                
                return True
            else:
                logger.error("❌ Failed to setup RAGFlow structure")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up RAGFlow structure: {e}")
            return False
    
    async def migrate_documents_to_ragflow(self) -> bool:
        """Migrate legal documents from MongoDB to RAGFlow."""
        try:
            logger.info("Migrating legal documents to RAGFlow...")
            
            # Fetch documents from MongoDB
            documents = await self.fetch_documents_from_mongodb()
            
            if not documents:
                logger.warning("No documents found in MongoDB")
                return False
            
            logger.info(f"Found {len(documents)} documents to migrate")
            
            # Group documents by target collection
            grouped_documents = self.group_documents_by_collection(documents)
            
            # Upload documents to each collection
            total_success = 0
            total_documents = len(documents)
            
            for collection_name, collection_docs in grouped_documents.items():
                logger.info(f"Uploading {len(collection_docs)} documents to {collection_name}...")
                
                success_count = await self.upload_collection_documents(collection_name, collection_docs)
                total_success += success_count
                
                logger.info(f"✅ Uploaded {success_count}/{len(collection_docs)} documents to {collection_name}")
            
            logger.info(f"✅ Migration completed: {total_success}/{total_documents} documents uploaded")
            
            return total_success > 0
            
        except Exception as e:
            logger.error(f"Error migrating documents: {e}")
            return False
    
    async def fetch_documents_from_mongodb(self) -> List[Dict[str, Any]]:
        """Fetch legal documents from MongoDB."""
        try:
            collection = self.mongodb_db["legal_documents"]
            
            # Fetch documents with processing status
            cursor = collection.find(
                {"processing.indexed": True},
                {
                    "document_id": 1,
                    "title": 1,
                    "document_type": 1,
                    "content": 1,
                    "year": 1,
                    "language": 1,
                    "metadata": 1,
                    "source": 1
                }
            )
            
            documents = await cursor.to_list(length=None)
            
            logger.info(f"Fetched {len(documents)} documents from MongoDB")
            
            return documents
            
        except Exception as e:
            logger.error(f"Error fetching documents from MongoDB: {e}")
            return []
    
    def group_documents_by_collection(self, documents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group documents by target RAGFlow collection."""
        grouped = {
            "income_tax_collection": [],
            "corporate_tax_collection": [],
            "vat_customs_collection": [],
            "tds_collection": [],
            "legal_precedents_collection": [],
            "forms_procedures_collection": []
        }
        
        # Document type mapping to collections
        type_mapping = {
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
        
        for doc in documents:
            doc_type = doc.get("document_type", "")
            target_collection = type_mapping.get(doc_type, "forms_procedures_collection")
            grouped[target_collection].append(doc)
        
        # Log distribution
        for collection, docs in grouped.items():
            if docs:
                logger.info(f"{collection}: {len(docs)} documents")
        
        return grouped
    
    async def upload_collection_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> int:
        """Upload documents to a specific RAGFlow collection."""
        success_count = 0
        
        for i, doc in enumerate(documents):
            try:
                # Prepare document content
                content = doc.get("content", "")
                if not content or len(content.strip()) < 50:
                    logger.warning(f"Skipping document with insufficient content: {doc.get('title', 'Unknown')}")
                    continue
                
                # Prepare metadata
                metadata = {
                    "document_id": doc.get("document_id"),
                    "document_type": doc.get("document_type"),
                    "year": doc.get("year"),
                    "language": doc.get("language"),
                    "original_title": doc.get("title"),
                    "keywords": doc.get("metadata", {}).get("keywords", []),
                    "tags": doc.get("metadata", {}).get("tags", [])
                }
                
                # Upload document
                success = await self.ragflow_client.upload_document(
                    collection_name=collection_name,
                    document_content=content,
                    document_name=f"{doc.get('document_id', f'doc_{i}')}_{doc.get('title', 'untitled')[:50]}",
                    metadata=metadata
                )
                
                if success:
                    success_count += 1
                    
                    # Update MongoDB with RAGFlow status
                    await self.update_document_ragflow_status(doc.get("document_id"), collection_name, True)
                
                # Progress logging
                if (i + 1) % 5 == 0:
                    logger.info(f"Processed {i + 1}/{len(documents)} documents in {collection_name}")
                
                # Add small delay to avoid overwhelming RAGFlow
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error uploading document {doc.get('title', 'Unknown')}: {e}")
                await self.update_document_ragflow_status(doc.get("document_id"), collection_name, False)
        
        return success_count
    
    async def update_document_ragflow_status(self, document_id: str, collection_name: str, success: bool):
        """Update document with RAGFlow upload status."""
        try:
            collection = self.mongodb_db["legal_documents"]
            
            update_data = {
                "processing.ragflow_uploaded": success,
                "processing.ragflow_collection": collection_name if success else None,
                "processing.last_processed": f"RAGFlow upload: {'success' if success else 'failed'}"
            }
            
            await collection.update_one(
                {"document_id": document_id},
                {"$set": update_data}
            )
            
        except Exception as e:
            logger.error(f"Error updating document status: {e}")
    
    async def validate_knowledge_base(self) -> bool:
        """Validate the setup knowledge base."""
        try:
            logger.info("Validating knowledge base setup...")
            
            # Get collection statistics
            collections = await self.ragflow_client.list_collections()
            
            validation_results = {
                "total_collections": len(collections),
                "collection_stats": {}
            }
            
            for collection in collections:
                collection_name = collection.get("name", "Unknown")
                
                # Get collection stats
                stats = await self.ragflow_client.get_collection_stats(collection_name)
                validation_results["collection_stats"][collection_name] = stats
                
                logger.info(f"Collection {collection_name}: {stats.get('document_count', 0)} documents")
            
            # Test search functionality
            test_queries = [
                "income tax calculation",
                "TDS rates 2024",
                "VAT exemption",
                "corporate tax provisions"
            ]
            
            search_test_results = []
            for query in test_queries:
                results = await self.ragflow_client.search(query, top_k=3)
                search_test_results.append({
                    "query": query,
                    "results_count": len(results),
                    "success": len(results) > 0
                })
                
                logger.info(f"Search test '{query}': {len(results)} results")
            
            # Validation summary
            total_documents = sum(
                stats.get('document_count', 0) 
                for stats in validation_results["collection_stats"].values()
            )
            
            successful_searches = sum(1 for test in search_test_results if test["success"])
            
            logger.info("📊 Validation Summary:")
            logger.info(f"  Total collections: {validation_results['total_collections']}")
            logger.info(f"  Total documents: {total_documents}")
            logger.info(f"  Successful search tests: {successful_searches}/{len(test_queries)}")
            
            # Determine overall success
            success = (
                validation_results["total_collections"] >= 5 and
                total_documents >= 100 and
                successful_searches >= len(test_queries) // 2
            )
            
            if success:
                logger.info("✅ Knowledge base validation passed")
            else:
                logger.warning("⚠️  Knowledge base validation has issues")
            
            return success
            
        except Exception as e:
            logger.error(f"Error validating knowledge base: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            await self.ragflow_client.close()
            self.mongodb_client.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Utility functions

async def setup_legal_knowledge_base() -> bool:
    """Setup the complete legal knowledge base."""
    setup = LegalKnowledgeBaseSetup()
    return await setup.setup_complete_knowledge_base()

async def test_knowledge_base_search():
    """Test the knowledge base search functionality."""
    async with RAGFlowClient() as client:
        test_queries = [
            "How to calculate income tax for salary income?",
            "What are the TDS rates for 2024?",
            "VAT registration requirements",
            "Corporate tax exemptions for export businesses",
            "Penalty for late filing of tax returns"
        ]
        
        print("🔍 Testing Knowledge Base Search...")
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            results = await client.search(query, top_k=3)
            
            if results:
                print(f"Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['document_name']} (Score: {result['score']:.3f})")
                    print(f"     Content preview: {result['content'][:100]}...")
            else:
                print("No results found")

async def main():
    """Main setup function."""
    print("🚀 Setting up RAGFlow Legal Knowledge Base...")
    
    # Setup knowledge base
    success = await setup_legal_knowledge_base()
    
    if success:
        print("✅ Knowledge base setup completed successfully!")
        
        # Test search functionality
        print("\n🔍 Testing search functionality...")
        await test_knowledge_base_search()
        
        print("\nNext steps:")
        print("1. Test agent framework integration")
        print("2. Implement base agent classes")
        print("3. Create micro-agents")
    else:
        print("❌ Knowledge base setup failed!")
        print("Check logs for error details.")

if __name__ == "__main__":
    asyncio.run(main())