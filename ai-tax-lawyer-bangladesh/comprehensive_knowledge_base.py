#!/usr/bin/env python3
"""
Comprehensive Knowledge Base - Week 1 Foundation
Integrates MongoDB, vector search, and document processing for senior lawyer foundation
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import pymongo
from simple_vector_system import SimpleKnowledgeBase, SimpleVectorEngine

logger = logging.getLogger(__name__)

class ComprehensiveKnowledgeBase:
    """
    Complete knowledge base combining database storage and vector search
    Foundation for senior lawyer level tax advisory system
    """
    
    def __init__(self, mongodb_url: str = None):
        self.mongodb_url = mongodb_url or "mongodb+srv://habib:Khurshida71@cluster0.qqlnw.mongodb.net/ai-tax-lawyer?retryWrites=true&w=majority&appName=Cluster0"
        self.database_name = "ai_tax_lawyer_bd"
        self.collection_name = "legal_documents"
        
        # Database components
        self.client = None
        self.db = None
        self.collection = None
        
        # Vector search components
        self.vector_kb = SimpleKnowledgeBase()
        self.documents_cache = []
        
        # Status flags
        self.db_connected = False
        self.vector_ready = False
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """Initialize the complete knowledge base system"""
        logger.info("🚀 Initializing Comprehensive Knowledge Base...")
        
        # Connect to database
        if not self._connect_database():
            return False
        
        # Load documents from database
        documents = self._load_documents_from_db()
        if not documents:
            logger.warning("⚠️ No documents found in database")
            return False
        
        # Initialize vector search
        if not self._initialize_vector_search(documents):
            return False
        
        self.is_initialized = True
        logger.info("✅ Comprehensive Knowledge Base initialized successfully")
        return True
    
    def _connect_database(self) -> bool:
        """Connect to MongoDB"""
        try:
            self.client = pymongo.MongoClient(self.mongodb_url)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            self.db_connected = True
            logger.info("✅ Database connected successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def _load_documents_from_db(self) -> List[Dict[str, Any]]:
        """Load all legal documents from database"""
        try:
            logger.info("📚 Loading documents from database...")
            
            # Get all documents
            cursor = self.collection.find({})
            documents = list(cursor)
            
            logger.info(f"✅ Loaded {len(documents)} documents from database")
            self.documents_cache = documents
            return documents
            
        except Exception as e:
            logger.error(f"❌ Failed to load documents: {e}")
            return []
    
    def _initialize_vector_search(self, documents: List[Dict[str, Any]]) -> bool:
        """Initialize vector search with documents"""
        try:
            logger.info("🔍 Initializing vector search system...")
            
            # Prepare documents for vector search
            processed_docs = []
            for doc in documents:
                # Create standardized document for vector search
                processed_doc = {
                    'document_id': str(doc.get('_id', doc.get('document_id', 'unknown'))),
                    'searchable_text': self._extract_searchable_text(doc),
                    'metadata': {
                        'filename': doc.get('metadata', {}).get('filename', 'unknown'),
                        'category': doc.get('metadata', {}).get('category', 'other'),
                        'source_file': doc.get('metadata', {}).get('source_file', ''),
                        'document_type': doc.get('document_type', 'legal_document')
                    },
                    'original_doc': doc
                }
                processed_docs.append(processed_doc)
            
            # Load into vector knowledge base
            self.vector_kb.load_documents(processed_docs)
            self.vector_ready = True
            
            logger.info("✅ Vector search system ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ Vector search initialization failed: {e}")
            return False
    
    def _extract_searchable_text(self, document: Dict[str, Any]) -> str:
        """Extract searchable text from database document"""
        text_parts = []
        
        # Common text fields
        text_fields = ['searchable_text', 'content', 'text', 'title', 'description']
        
        for field in text_fields:
            if field in document and isinstance(document[field], str):
                text_parts.append(document[field])
        
        # Extract from original content if available
        if 'original_content' in document:
            self._extract_text_recursive(document['original_content'], text_parts)
        
        return ' '.join(text_parts)
    
    def _extract_text_recursive(self, obj: Any, text_parts: List[str]):
        """Recursively extract text from nested structures"""
        if isinstance(obj, str) and len(obj) > 20:
            text_parts.append(obj)
        elif isinstance(obj, dict):
            for value in obj.values():
                self._extract_text_recursive(value, text_parts)
        elif isinstance(obj, list):
            for item in obj:
                self._extract_text_recursive(item, text_parts)
    
    def search(self, query: str, search_type: str = "hybrid", limit: int = 5) -> Dict[str, Any]:
        """
        Comprehensive search combining database and vector search
        
        Args:
            query: Search query
            search_type: "vector", "database", or "hybrid" 
            limit: Maximum results to return
        """
        if not self.is_initialized:
            return {
                'success': False,
                'error': 'Knowledge base not initialized'
            }
        
        results = {
            'query': query,
            'search_type': search_type,
            'vector_results': [],
            'database_results': [],
            'combined_results': [],
            'total_found': 0
        }
        
        try:
            # Vector search
            if search_type in ["vector", "hybrid"]:
                vector_results = self.vector_kb.search(query, top_k=limit)
                results['vector_results'] = vector_results
            
            # Database search
            if search_type in ["database", "hybrid"]:
                db_results = self._database_text_search(query, limit)
                results['database_results'] = db_results
            
            # Combine results for hybrid search
            if search_type == "hybrid":
                combined = self._combine_search_results(
                    results['vector_results'], 
                    results['database_results']
                )
                results['combined_results'] = combined[:limit]
            elif search_type == "vector":
                results['combined_results'] = results['vector_results']
            else:
                results['combined_results'] = results['database_results']
            
            results['total_found'] = len(results['combined_results'])
            results['success'] = True
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def _database_text_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Perform text search in database"""
        try:
            # MongoDB text search
            search_results = self.collection.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            db_results = []
            for doc in search_results:
                result = {
                    'document': {
                        'document_id': str(doc['_id']),
                        'metadata': doc.get('metadata', {}),
                        'searchable_text': self._extract_searchable_text(doc)
                    },
                    'score': doc.get('score', 0) * 100,  # Convert to percentage
                    'source': 'database'
                }
                db_results.append(result)
            
            return db_results
            
        except Exception as e:
            logger.error(f"❌ Database search failed: {e}")
            return []
    
    def _combine_search_results(self, vector_results: List[Dict], db_results: List[Dict]) -> List[Dict]:
        """Combine and deduplicate search results"""
        combined = []
        seen_docs = set()
        
        # Add vector results first (usually more relevant)
        for result in vector_results:
            doc_id = result['document']['document_id']
            if doc_id not in seen_docs:
                result['sources'] = ['vector']
                combined.append(result)
                seen_docs.add(doc_id)
        
        # Add unique database results
        for result in db_results:
            doc_id = result['document']['document_id']
            if doc_id not in seen_docs:
                result['sources'] = ['database']
                combined.append(result)
                seen_docs.add(doc_id)
            else:
                # If already exists, mark as found in both
                for existing in combined:
                    if existing['document']['document_id'] == doc_id:
                        existing['sources'].append('database')
                        # Boost score for documents found in both
                        existing['score'] = min(existing['score'] * 1.2, 100)
                        break
        
        # Sort by score
        combined.sort(key=lambda x: x['score'], reverse=True)
        return combined
    
    def chat(self, question: str, context_limit: int = 3) -> Dict[str, Any]:
        """Advanced chat functionality with comprehensive search"""
        if not self.is_initialized:
            return {
                'success': False,
                'error': 'Knowledge base not initialized'
            }
        
        try:
            # Use hybrid search for best results
            search_results = self.search(question, search_type="hybrid", limit=context_limit)
            
            if not search_results['success'] or not search_results['combined_results']:
                return {
                    'success': True,
                    'question': question,
                    'answer': "I couldn't find specific information about your question in the legal documents. Please try rephrasing your query or being more specific.",
                    'sources': [],
                    'search_results': search_results
                }
            
            # Generate comprehensive answer
            answer_parts = []
            sources = []
            
            for result in search_results['combined_results']:
                # Extract snippets if available
                if 'snippets' in result and result['snippets']:
                    answer_parts.extend(result['snippets'][:2])
                else:
                    # Extract snippet from document text
                    text = result['document']['searchable_text']
                    snippet = self._extract_simple_snippet(text, question)
                    if snippet:
                        answer_parts.append(snippet)
                
                # Add source information
                sources.append({
                    'filename': result['document']['metadata'].get('filename', 'Unknown'),
                    'category': result['document']['metadata'].get('category', 'other'),
                    'score': round(result['score'], 2),
                    'found_in': result.get('sources', ['unknown'])
                })
            
            # Create comprehensive answer
            if answer_parts:
                answer = "Based on Bangladesh tax laws and regulations:\n\n" + "\n\n".join(answer_parts[:4])
            else:
                answer = "I found relevant documents but couldn't extract specific information. Please refer to the source documents for detailed information."
            
            return {
                'success': True,
                'question': question,
                'answer': answer,
                'sources': sources,
                'search_results': search_results,
                'total_sources': len(sources)
            }
            
        except Exception as e:
            logger.error(f"❌ Chat functionality failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_simple_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """Extract a simple snippet containing query terms"""
        import re
        
        query_words = set(query.lower().split())
        sentences = re.split(r'[।\.!?]+', text)
        
        for sentence in sentences:
            if len(sentence.strip()) < 30:
                continue
            
            sentence_words = set(sentence.lower().split())
            if query_words & sentence_words:  # If there's any overlap
                snippet = sentence.strip()
                if len(snippet) > max_length:
                    snippet = snippet[:max_length] + "..."
                return snippet
        
        # Fallback: return first part of text
        return text[:max_length] + "..." if len(text) > max_length else text
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the knowledge base"""
        stats = {
            'initialized': self.is_initialized,
            'database_connected': self.db_connected,
            'vector_search_ready': self.vector_ready,
            'total_documents': 0,
            'categories': {},
            'database_stats': {},
            'vector_stats': {}
        }
        
        if self.db_connected:
            try:
                # Database statistics
                total_docs = self.collection.count_documents({})
                stats['total_documents'] = total_docs
                
                # Category breakdown
                pipeline = [
                    {"$group": {"_id": "$metadata.category", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ]
                category_results = list(self.collection.aggregate(pipeline))
                stats['categories'] = {item['_id']: item['count'] for item in category_results}
                
                stats['database_stats'] = {
                    'collection_name': self.collection_name,
                    'total_documents': total_docs,
                    'indexes': len(list(self.collection.list_indexes()))
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to get database stats: {e}")
        
        if self.vector_ready:
            stats['vector_stats'] = self.vector_kb.vector_engine.get_stats()
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health = {
            'overall_status': 'healthy',
            'components': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Database health
        try:
            if self.db_connected:
                self.client.admin.command('ping')
                health['components']['database'] = {
                    'status': 'healthy',
                    'connection': 'active',
                    'documents': self.collection.count_documents({})
                }
            else:
                health['components']['database'] = {
                    'status': 'disconnected',
                    'connection': 'failed'
                }
                health['overall_status'] = 'degraded'
        except Exception as e:
            health['components']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health['overall_status'] = 'unhealthy'
        
        # Vector search health
        health['components']['vector_search'] = {
            'status': 'healthy' if self.vector_ready else 'not_ready',
            'documents_loaded': len(self.documents_cache)
        }
        
        # Overall initialization
        health['components']['initialization'] = {
            'status': 'complete' if self.is_initialized else 'incomplete'
        }
        
        return health

def main():
    """Test the comprehensive knowledge base"""
    print("🏗️ Testing Comprehensive Knowledge Base - Week 1 Foundation")
    
    # Initialize knowledge base
    kb = ComprehensiveKnowledgeBase()
    
    if not kb.initialize():
        print("❌ Failed to initialize knowledge base")
        return
    
    # Show statistics
    stats = kb.get_statistics()
    print(f"\n📊 Knowledge Base Statistics:")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Categories: {dict(list(stats['categories'].items())[:5])}")  # Show top 5
    print(f"   Vector vocabulary: {stats['vector_stats'].get('vocabulary_size', 0)} terms")
    
    # Test different search types
    test_query = "income tax rates Bangladesh"
    
    print(f"\n🔍 Testing Search: '{test_query}'")
    
    # Vector search
    print("\n   📈 Vector Search:")
    vector_results = kb.search(test_query, search_type="vector", limit=3)
    for i, result in enumerate(vector_results['combined_results'], 1):
        print(f"   {i}. Score: {result['score']:.1f}% - {result['document']['metadata']['filename']}")
    
    # Database search
    print("\n   🗄️ Database Search:")
    db_results = kb.search(test_query, search_type="database", limit=3)
    for i, result in enumerate(db_results['combined_results'], 1):
        print(f"   {i}. Score: {result['score']:.1f}% - {result['document']['metadata']['filename']}")
    
    # Hybrid search
    print("\n   🔄 Hybrid Search:")
    hybrid_results = kb.search(test_query, search_type="hybrid", limit=3)
    for i, result in enumerate(hybrid_results['combined_results'], 1):
        sources_str = "+".join(result.get('sources', ['unknown']))
        print(f"   {i}. Score: {result['score']:.1f}% ({sources_str}) - {result['document']['metadata']['filename']}")
    
    # Test chat functionality
    print(f"\n💬 Chat Test:")
    question = "What are the current income tax exemption limits?"
    response = kb.chat(question)
    
    if response['success']:
        print(f"Q: {question}")
        print(f"A: {response['answer'][:300]}...")
        print(f"Sources: {len(response['sources'])} documents")
    else:
        print(f"❌ Chat failed: {response['error']}")
    
    # Health check
    health = kb.health_check()
    print(f"\n🏥 Health Check: {health['overall_status']}")
    for component, status in health['components'].items():
        print(f"   {component}: {status['status']}")
    
    print("\n✅ Comprehensive Knowledge Base test complete!")

if __name__ == "__main__":
    main()