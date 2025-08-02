#!/usr/bin/env python3
"""
Database Configuration and Connection Management
Handles MongoDB Atlas connections and operations
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Database manager for MongoDB Atlas
    Handles connections, collections, and basic operations
    """
    
    def __init__(self, connection_string: str = None, database_name: str = None):
        self.connection_string = connection_string or self._get_connection_string()
        self.database_name = database_name or "ai_tax_lawyer_bd"
        self.client: Optional[MongoClient] = None
        self.db = None
        self._connected = False
    
    def _get_connection_string(self) -> str:
        """Get MongoDB connection string from environment or default"""
        # Try to read from .env file
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('MONGODB_URL='):
                        return line.split('=', 1)[1].strip()
        
        # Fallback to environment variable or default
        return os.getenv('MONGODB_URL', 
                        'mongodb+srv://habib:Khurshida71@cluster0.qqlnw.mongodb.net/ai-tax-lawyer?retryWrites=true&w=majority&appName=Cluster0')
    
    def connect(self) -> bool:
        """Establish database connection"""
        if not PYMONGO_AVAILABLE:
            logger.error("PyMongo not available. Install with: pip install pymongo")
            return False
        
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self._connected = True
            
            logger.info(f"✅ Connected to MongoDB database: {self.database_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected database error: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Database connection closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._connected and self.client is not None
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if not self.is_connected:
            raise ConnectionError("Database not connected")
        return self.db[collection_name]
    
    def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return {
                        'status': 'disconnected',
                        'error': 'Failed to connect to database'
                    }
            
            # Test basic operations
            result = self.client.admin.command('ping')
            
            # Get database stats
            stats = self.db.command('dbstats')
            
            return {
                'status': 'healthy',
                'connected': True,
                'database': self.database_name,
                'collections': self.db.list_collection_names(),
                'stats': {
                    'collections_count': stats.get('collections', 0),
                    'data_size': stats.get('dataSize', 0),
                    'storage_size': stats.get('storageSize', 0)
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

class LegalDocumentStore:
    """
    Specialized store for legal documents
    Handles tax law documents with proper indexing
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.collection_name = "legal_documents"
        self._collection = None
    
    @property
    def collection(self):
        """Get legal documents collection"""
        if not self._collection:
            self._collection = self.db_manager.get_collection(self.collection_name)
        return self._collection
    
    def ensure_indexes(self):
        """Create necessary indexes for legal documents"""
        try:
            # Text search index
            self.collection.create_index([
                ("title", "text"),
                ("content", "text"),
                ("keywords", "text")
            ], name="text_search_index")
            
            # Compound indexes for filtering
            self.collection.create_index([
                ("document_type", 1),
                ("year", -1)
            ], name="type_year_index")
            
            self.collection.create_index([
                ("act_name", 1),
                ("section", 1)
            ], name="act_section_index")
            
            # Date index
            self.collection.create_index([
                ("created_at", -1)
            ], name="created_date_index")
            
            logger.info("✅ Legal document indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {e}")
    
    def insert_document(self, document: Dict[str, Any]) -> str:
        """Insert a legal document"""
        try:
            # Add metadata
            document['created_at'] = datetime.now()
            document['updated_at'] = datetime.now()
            
            result = self.collection.insert_one(document)
            logger.info(f"Document inserted with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to insert document: {e}")
            raise
    
    def insert_many_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple legal documents"""
        try:
            # Add metadata to all documents
            now = datetime.now()
            for doc in documents:
                doc['created_at'] = now
                doc['updated_at'] = now
            
            result = self.collection.insert_many(documents)
            logger.info(f"Inserted {len(result.inserted_ids)} documents")
            return [str(id) for id in result.inserted_ids]
            
        except Exception as e:
            logger.error(f"Failed to insert documents: {e}")
            raise
    
    def search_documents(self, 
                        query: str = None,
                        document_type: str = None,
                        act_name: str = None,
                        limit: int = 10) -> List[Dict[str, Any]]:
        """Search legal documents"""
        try:
            filter_criteria = {}
            
            # Text search
            if query:
                filter_criteria['$text'] = {'$search': query}
            
            # Type filter
            if document_type:
                filter_criteria['document_type'] = document_type
            
            # Act filter
            if act_name:
                filter_criteria['act_name'] = {"$regex": act_name, "$options": "i"}
            
            # Execute search
            cursor = self.collection.find(filter_criteria).limit(limit)
            
            # If text search, sort by score
            if query:
                cursor = cursor.sort([("score", {"$meta": "textScore"})])
            else:
                cursor = cursor.sort([("created_at", -1)])
            
            return list(cursor)
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about legal documents"""
        try:
            total_docs = self.collection.count_documents({})
            
            # Get document types
            types_pipeline = [
                {"$group": {"_id": "$document_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            types = list(self.collection.aggregate(types_pipeline))
            
            # Get acts
            acts_pipeline = [
                {"$group": {"_id": "$act_name", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            acts = list(self.collection.aggregate(acts_pipeline))
            
            return {
                'total_documents': total_docs,
                'document_types': types,
                'top_acts': acts,
                'collection_name': self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'error': str(e)}

# Singleton database manager
_db_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Get singleton database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.connect()
    return _db_manager

def get_legal_document_store() -> LegalDocumentStore:
    """Get legal document store instance"""
    db_manager = get_database_manager()
    store = LegalDocumentStore(db_manager)
    store.ensure_indexes()
    return store

# Example usage
if __name__ == "__main__":
    # Test database connection
    db_manager = get_database_manager()
    
    if db_manager.is_connected:
        print("✅ Database connection successful")
        
        # Test legal document store
        doc_store = get_legal_document_store()
        stats = doc_store.get_document_stats()
        print(f"📊 Database stats: {stats}")
        
        # Health check
        health = db_manager.health_check()
        print(f"🏥 Health check: {health['status']}")
        
    else:
        print("❌ Database connection failed")