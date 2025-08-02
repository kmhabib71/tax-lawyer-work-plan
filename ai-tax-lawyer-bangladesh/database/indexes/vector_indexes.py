"""
Vector indexes configuration for MongoDB Atlas Vector Search.
"""
from typing import Dict, Any, List
import pymongo
from pymongo import MongoClient
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class VectorIndexManager:
    """Manages vector indexes for MongoDB Atlas Vector Search."""
    
    def __init__(self, client: MongoClient):
        self.client = client
        self.database = client[settings.mongodb_database]
    
    def create_all_vector_indexes(self) -> bool:
        """Create all vector indexes for the application."""
        try:
            # Legal documents vector index
            self.create_legal_documents_vector_index()
            
            # Document chunks vector index  
            self.create_document_chunks_vector_index()
            
            # Legal precedents vector index
            self.create_legal_precedents_vector_index()
            
            logger.info("All vector indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating vector indexes: {e}")
            return False
    
    def create_legal_documents_vector_index(self):
        """Create vector index for legal documents collection."""
        collection = self.database["legal_documents"]
        
        vector_index_definition = {
            "fields": [
                {
                    "type": "vector",
                    "path": "content_embedding",
                    "numDimensions": 1536,
                    "similarity": "cosine"
                },
                {
                    "type": "filter",
                    "path": "document_type"
                },
                {
                    "type": "filter", 
                    "path": "year"
                },
                {
                    "type": "filter",
                    "path": "language"
                },
                {
                    "type": "filter",
                    "path": "metadata.status"
                }
            ]
        }
        
        try:
            collection.create_search_index(
                name="legal_documents_vector_index",
                definition=vector_index_definition
            )
            logger.info("Created legal_documents_vector_index")
        except Exception as e:
            logger.warning(f"legal_documents_vector_index might already exist: {e}")
    
    def create_document_chunks_vector_index(self):
        """Create vector index for document chunks collection."""
        collection = self.database["document_embeddings"]
        
        vector_index_definition = {
            "fields": [
                {
                    "type": "vector",
                    "path": "chunk_embedding",
                    "numDimensions": 1536,
                    "similarity": "cosine"
                },
                {
                    "type": "filter",
                    "path": "document_id"
                },
                {
                    "type": "filter",
                    "path": "chunk_type"
                },
                {
                    "type": "filter",
                    "path": "relevance_score"
                }
            ]
        }
        
        try:
            collection.create_search_index(
                name="document_chunks_vector_index",
                definition=vector_index_definition
            )
            logger.info("Created document_chunks_vector_index")
        except Exception as e:
            logger.warning(f"document_chunks_vector_index might already exist: {e}")
    
    def create_legal_precedents_vector_index(self):
        """Create vector index for legal precedents collection."""
        collection = self.database["legal_precedents"]
        
        vector_index_definition = {
            "fields": [
                {
                    "type": "vector",
                    "path": "case_embedding",
                    "numDimensions": 1536,
                    "similarity": "cosine"
                },
                {
                    "type": "filter",
                    "path": "case_type"
                },
                {
                    "type": "filter",
                    "path": "court_level"
                },
                {
                    "type": "filter", 
                    "path": "decision_year"
                },
                {
                    "type": "filter",
                    "path": "relevance_category"
                }
            ]
        }
        
        try:
            collection.create_search_index(
                name="legal_precedents_vector_index",
                definition=vector_index_definition
            )
            logger.info("Created legal_precedents_vector_index")
        except Exception as e:
            logger.warning(f"legal_precedents_vector_index might already exist: {e}")

class TextIndexManager:
    """Manages text indexes for traditional MongoDB text search."""
    
    def __init__(self, client: MongoClient):
        self.client = client
        self.database = client[settings.mongodb_database]
    
    def create_all_text_indexes(self) -> bool:
        """Create all text indexes for the application."""
        try:
            # Legal documents text search
            self.create_legal_documents_text_index()
            
            # Tax rules text search
            self.create_tax_rules_text_index()
            
            # Agent logs text search
            self.create_agent_logs_text_index()
            
            logger.info("All text indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating text indexes: {e}")
            return False
    
    def create_legal_documents_text_index(self):
        """Create text index for legal documents."""
        collection = self.database["legal_documents"]
        
        try:
            collection.create_index([
                ("title", "text"),
                ("content", "text"),
                ("metadata.keywords", "text")
            ], name="legal_documents_text_index")
            logger.info("Created legal_documents_text_index")
        except Exception as e:
            logger.warning(f"legal_documents_text_index might already exist: {e}")
    
    def create_tax_rules_text_index(self):
        """Create text index for tax rules."""
        collection = self.database["tax_rules"]
        
        try:
            collection.create_index([
                ("rule_name", "text"),
                ("description", "text"),
                ("keywords", "text")
            ], name="tax_rules_text_index")
            logger.info("Created tax_rules_text_index")
        except Exception as e:
            logger.warning(f"tax_rules_text_index might already exist: {e}")
    
    def create_agent_logs_text_index(self):
        """Create text index for agent logs."""
        collection = self.database["agent_logs"]
        
        try:
            collection.create_index([
                ("query", "text"),
                ("response", "text"),
                ("error_message", "text")
            ], name="agent_logs_text_index")
            logger.info("Created agent_logs_text_index")
        except Exception as e:
            logger.warning(f"agent_logs_text_index might already exist: {e}")

class CompoundIndexManager:
    """Manages compound indexes for optimized queries."""
    
    def __init__(self, client: MongoClient):
        self.client = client
        self.database = client[settings.mongodb_database]
    
    def create_all_compound_indexes(self) -> bool:
        """Create all compound indexes for the application."""
        try:
            # Legal documents compound indexes
            self.create_legal_documents_compound_indexes()
            
            # Tax calculations compound indexes
            self.create_tax_calculations_compound_indexes()
            
            # Agent performance compound indexes
            self.create_agent_performance_compound_indexes()
            
            # User session compound indexes
            self.create_user_session_compound_indexes()
            
            logger.info("All compound indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating compound indexes: {e}")
            return False
    
    def create_legal_documents_compound_indexes(self):
        """Create compound indexes for legal documents."""
        collection = self.database["legal_documents"]
        
        compound_indexes = [
            # Document type and year
            ([("document_type", 1), ("year", 1), ("metadata.status", 1)], 
             "legal_docs_type_year_status"),
            
            # Language and effective date
            ([("language", 1), ("metadata.effective_date", 1)], 
             "legal_docs_lang_effective"),
            
            # Processing status
            ([("processing.indexed", 1), ("processing.embedded", 1)], 
             "legal_docs_processing_status"),
            
            # Usage statistics
            ([("usage_stats.query_count", -1), ("usage_stats.relevance_score", -1)], 
             "legal_docs_usage_stats")
        ]
        
        for index_spec, index_name in compound_indexes:
            try:
                collection.create_index(index_spec, name=index_name)
                logger.info(f"Created compound index: {index_name}")
            except Exception as e:
                logger.warning(f"Compound index {index_name} might already exist: {e}")
    
    def create_tax_calculations_compound_indexes(self):
        """Create compound indexes for tax calculations."""
        collection = self.database["calculation_history"]
        
        compound_indexes = [
            # User and calculation type
            ([("user_id", 1), ("calculation_type", 1), ("created_at", -1)], 
             "calc_user_type_date"),
            
            # Tax year and status
            ([("input_data.tax_year", 1), ("status", 1)], 
             "calc_year_status"),
            
            # Performance metrics
            ([("performance.calculation_time_ms", 1), ("calculation_method.confidence_score", -1)], 
             "calc_performance_confidence"),
            
            # Validation status
            ([("validation.validated", 1), ("validation.validation_score", -1)], 
             "calc_validation_status")
        ]
        
        for index_spec, index_name in compound_indexes:
            try:
                collection.create_index(index_spec, name=index_name)
                logger.info(f"Created compound index: {index_name}")
            except Exception as e:
                logger.warning(f"Compound index {index_name} might already exist: {e}")
    
    def create_agent_performance_compound_indexes(self):
        """Create compound indexes for agent performance."""
        collection = self.database["agent_logs"]
        
        compound_indexes = [
            # Agent performance tracking
            ([("agent_id", 1), ("timestamp", -1), ("performance_score", -1)], 
             "agent_perf_tracking"),
            
            # Query type and response time
            ([("query_type", 1), ("response_time_ms", 1)], 
             "agent_query_response_time"),
            
            # Error tracking
            ([("status", 1), ("error_code", 1), ("timestamp", -1)], 
             "agent_error_tracking"),
            
            # Success rate tracking
            ([("agent_id", 1), ("status", 1), ("created_at", -1)], 
             "agent_success_tracking")
        ]
        
        for index_spec, index_name in compound_indexes:
            try:
                collection.create_index(index_spec, name=index_name)
                logger.info(f"Created compound index: {index_name}")
            except Exception as e:
                logger.warning(f"Compound index {index_name} might already exist: {e}")
    
    def create_user_session_compound_indexes(self):
        """Create compound indexes for user sessions."""
        collection = self.database["user_sessions"]
        
        compound_indexes = [
            # User session tracking
            ([("user_id", 1), ("created_at", -1)], 
             "user_session_tracking"),
            
            # Session duration and activity
            ([("session_duration", -1), ("query_count", -1)], 
             "session_activity"),
            
            # Session status and timestamp
            ([("status", 1), ("last_activity", -1)], 
             "session_status_activity")
        ]
        
        for index_spec, index_name in compound_indexes:
            try:
                collection.create_index(index_spec, name=index_name)
                logger.info(f"Created compound index: {index_name}")
            except Exception as e:
                logger.warning(f"Compound index {index_name} might already exist: {e}")

def create_all_indexes(client: MongoClient) -> bool:
    """Create all indexes for the application."""
    try:
        # Create vector indexes
        vector_manager = VectorIndexManager(client)
        vector_success = vector_manager.create_all_vector_indexes()
        
        # Create text indexes
        text_manager = TextIndexManager(client)
        text_success = text_manager.create_all_text_indexes()
        
        # Create compound indexes
        compound_manager = CompoundIndexManager(client)
        compound_success = compound_manager.create_all_compound_indexes()
        
        return vector_success and text_success and compound_success
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        return False

if __name__ == "__main__":
    # Test index creation
    from pymongo import MongoClient
    
    client = MongoClient(settings.mongodb_url)
    success = create_all_indexes(client)
    
    if success:
        print("✅ All indexes created successfully")
    else:
        print("❌ Error creating some indexes")
    
    client.close()