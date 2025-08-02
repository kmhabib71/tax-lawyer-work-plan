"""
Configuration settings for AI Tax Lawyer Bangladesh application.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "ai_tax_lawyer_bd"
    mongodb_test_database: str = "ai_tax_lawyer_bd_test"
    
    # RAGFlow Configuration
    ragflow_api_url: str = "http://localhost:9380"
    ragflow_api_key: str = ""
    ragflow_knowledge_base: str = "bd_tax_law_kb"
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_embedding_model: str = "text-embedding-ada-002"
    openai_max_tokens: int = 4000
    openai_temperature: float = 0.1
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_debug: bool = True
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    sentry_dsn: Optional[str] = None
    
    # Agent Configuration
    max_concurrent_agents: int = 10
    agent_timeout: int = 30
    agent_retry_attempts: int = 3
    
    # Performance Configuration
    max_query_length: int = 10000
    max_response_length: int = 50000
    rate_limit_per_minute: int = 100
    
    # Development Configuration
    environment: str = "development"
    debug_agents: bool = True
    enable_metrics: bool = True
    
    # Bengali Language Configuration
    bengali_model_path: str = "models/bengali_nlp"
    translation_api_key: str = ""
    
    # Form Processing Configuration
    form_upload_max_size: int = 10485760  # 10MB
    supported_formats: List[str] = ["pdf", "docx", "xlsx"]
    
    # Legal Document Configuration
    legal_docs_path: str = "data/legal_documents/"
    embeddings_cache_path: str = "data/embeddings/"
    processed_data_path: str = "data/processed_data/"
    
    # Project Paths
    @property
    def project_root(self) -> Path:
        return Path(__file__).parent.parent
    
    @property
    def data_path(self) -> Path:
        return self.project_root / "data"
    
    @property
    def logs_path(self) -> Path:
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Agent-specific configurations
class AgentConfig:
    """Configuration for different agent types."""
    
    SENIOR_AGENT_CONFIG = {
        "max_context_length": 8000,
        "decision_threshold": 0.8,
        "coordination_timeout": 60,
        "llm_usage_percentage": 30
    }
    
    JUNIOR_AGENT_CONFIGS = {
        "income_tax_agent": {
            "rule_coverage": 0.85,
            "llm_threshold": 0.7,
            "specialization": ["personal_income", "tds", "rebates"],
            "ragflow_collections": ["income_tax_collection", "tds_collection"]
        },
        "corporate_tax_agent": {
            "rule_coverage": 0.80,
            "llm_threshold": 0.7,
            "specialization": ["corporate_income", "business_expenses", "depreciation"],
            "ragflow_collections": ["corporate_tax_collection", "business_rules"]
        },
        "vat_customs_agent": {
            "rule_coverage": 0.75,
            "llm_threshold": 0.7,
            "specialization": ["vat_calculation", "customs_duty", "trade_exemptions"],
            "ragflow_collections": ["vat_customs_collection", "trade_policies"]
        },
        "tds_agent": {
            "rule_coverage": 0.90,
            "llm_threshold": 0.8,
            "specialization": ["tds_rates", "withholding", "certificates"],
            "ragflow_collections": ["tds_collection", "withholding_circulars"]
        },
        "form_automation_agent": {
            "rule_coverage": 0.95,
            "llm_threshold": 0.9,
            "specialization": ["ereturn_forms", "validation", "submission"],
            "ragflow_collections": ["forms_procedures_collection"]
        },
        "legal_research_agent": {
            "rule_coverage": 0.30,
            "llm_threshold": 0.5,
            "specialization": ["precedents", "case_law", "citations"],
            "ragflow_collections": ["legal_precedents_collection", "all_collections"]
        }
    }
    
    MICRO_AGENT_CONFIGS = {
        "tax_slab_calculator": {"rule_coverage": 1.0, "response_time_ms": 50},
        "rebate_exemption_agent": {"rule_coverage": 0.95, "response_time_ms": 100},
        "penalty_calculator": {"rule_coverage": 1.0, "response_time_ms": 75},
        "rate_manager": {"rule_coverage": 1.0, "response_time_ms": 25},
        "currency_converter": {"rule_coverage": 1.0, "response_time_ms": 100},
        "deadline_manager": {"rule_coverage": 1.0, "response_time_ms": 50}
    }

# Database configuration
class DatabaseConfig:
    """Database-specific configurations."""
    
    COLLECTIONS = {
        "legal_documents": {
            "indexes": ["content_vector", "document_type", "year", "section"],
            "size_estimate_gb": 2
        },
        "document_embeddings": {
            "indexes": ["vector_index", "document_id", "chunk_id"],
            "size_estimate_gb": 5
        },
        "tax_rules": {
            "indexes": ["rule_type", "effective_date", "category"],
            "size_estimate_mb": 100
        },
        "tax_slabs": {
            "indexes": ["year", "tax_type", "income_range"],
            "size_estimate_mb": 50
        },
        "exemptions_rebates": {
            "indexes": ["type", "category", "effective_date"],
            "size_estimate_mb": 200
        },
        "user_sessions": {
            "indexes": ["user_id", "session_id", "timestamp"],
            "size_estimate_gb": 1
        },
        "calculation_history": {
            "indexes": ["user_id", "calculation_type", "date"],
            "size_estimate_gb": 2
        },
        "agent_logs": {
            "indexes": ["agent_id", "timestamp", "performance_score"],
            "size_estimate_mb": 500
        },
        "agent_cache": {
            "indexes": ["agent_id", "query_hash", "expiry"],
            "size_estimate_gb": 1
        },
        "form_templates": {
            "indexes": ["form_type", "version", "year"],
            "size_estimate_mb": 100
        },
        "compliance_tracking": {
            "indexes": ["user_id", "deadline", "status"],
            "size_estimate_mb": 300
        }
    }
    
    VECTOR_INDEXES = {
        "legal_documents_vector": {
            "field": "content_embedding",
            "dimensions": 1536,
            "similarity": "cosine"
        },
        "document_chunks_vector": {
            "field": "chunk_embedding", 
            "dimensions": 1536,
            "similarity": "cosine"
        },
        "legal_precedents_vector": {
            "field": "case_embedding",
            "dimensions": 1536,
            "similarity": "cosine"
        }
    }

# RAGFlow configuration
class RAGFlowConfig:
    """RAGFlow-specific configurations."""
    
    COLLECTIONS = {
        "income_tax_collection": {
            "chunk_size": 1000,
            "overlap": 200,
            "retrieval_strategy": "hybrid_search"
        },
        "corporate_tax_collection": {
            "chunk_size": 1200,
            "overlap": 150,
            "retrieval_strategy": "semantic_search"
        },
        "vat_customs_collection": {
            "chunk_size": 800,
            "overlap": 100,
            "retrieval_strategy": "keyword_semantic_hybrid"
        },
        "tds_collection": {
            "chunk_size": 600,
            "overlap": 100,
            "retrieval_strategy": "exact_match_semantic"
        },
        "legal_precedents_collection": {
            "chunk_size": 1500,
            "overlap": 300,
            "retrieval_strategy": "similarity_search"
        },
        "forms_procedures_collection": {
            "chunk_size": 500,
            "overlap": 50,
            "retrieval_strategy": "structured_search"
        }
    }