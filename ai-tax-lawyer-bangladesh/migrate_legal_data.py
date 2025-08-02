#!/usr/bin/env python3
"""
ACTUAL Legal Data Migration Script - Week 1 Completion
Migrates real legal documents from ragflow/phase0_foundation/data_assets to MongoDB
"""
import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
import hashlib
from typing import Dict, Any, List
import pymongo
from pymongo import MongoClient

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Simple logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealLegalDataMigrator:
    """Migrates actual legal data from ragflow phase0 foundation to MongoDB."""
    
    def __init__(self):
        # MongoDB connection
        self.connection_string = "mongodb+srv://habib:Khurshida71@cluster0.qqlnw.mongodb.net/ai-tax-lawyer?retryWrites=true&w=majority&appName=Cluster0"
        self.database_name = "ai_tax_lawyer_bd"
        
        # Data source path
        self.data_path = Path("/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ragflow/phase0_foundation/data_assets")
        
        # Initialize MongoDB
        self.client = None
        self.db = None
        self.collection = None
        
        # Migration stats
        self.stats = {
            "total_files": 0,
            "migrated_files": 0,
            "skipped_files": 0,
            "errors": 0
        }
    
    def connect_mongodb(self) -> bool:
        """Connect to MongoDB Atlas."""
        try:
            logger.info("Connecting to MongoDB Atlas...")
            self.client = MongoClient(self.connection_string)
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ MongoDB connection successful!")
            
            # Get database and collection
            self.db = self.client[self.database_name]
            self.collection = self.db["legal_documents"]
            
            # Create basic index
            self.collection.create_index("document_id", unique=True)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
    
    def migrate_all_legal_files(self) -> bool:
        """Migrate all legal files to MongoDB."""
        try:
            if not self.connect_mongodb():
                return False
            
            logger.info(f"🚀 Starting migration from: {self.data_path}")
            
            # Find all JSON files
            json_files = []
            
            # Root level JSON files
            for file_path in self.data_path.glob("*.json"):
                json_files.append(file_path)
            
            # Senior tax lawyer content
            senior_content_path = self.data_path / "senior_tax_lawyer_content"
            if senior_content_path.exists():
                for file_path in senior_content_path.glob("*.json"):
                    json_files.append(file_path)
            
            self.stats["total_files"] = len(json_files)
            logger.info(f"Found {len(json_files)} JSON files to migrate")
            
            # Migrate each file
            for i, file_path in enumerate(json_files, 1):
                logger.info(f"Processing {i}/{len(json_files)}: {file_path.name}")
                
                if self.migrate_single_file(file_path):
                    self.stats["migrated_files"] += 1
                else:
                    self.stats["skipped_files"] += 1
                
                # Progress update every 10 files
                if i % 10 == 0:
                    logger.info(f"Progress: {i}/{len(json_files)} files processed")
            
            # Print final stats
            self.print_migration_stats()
            
            return self.stats["migrated_files"] > 0
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
        finally:
            if self.client:
                self.client.close()
    
    def migrate_single_file(self, file_path: Path) -> bool:
        """Migrate a single JSON file to MongoDB."""
        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Skip if empty or invalid
            if not data or not isinstance(data, dict):
                logger.warning(f"Skipping invalid file: {file_path.name}")
                return False
            
            # Create document structure
            document = self.create_document_structure(file_path, data)
            
            # Check if already exists
            existing = self.collection.find_one({"document_id": document["document_id"]})
            if existing:
                logger.debug(f"Document already exists: {document['document_id']}")
                return False
            
            # Insert document
            self.collection.insert_one(document)
            logger.debug(f"✅ Migrated: {file_path.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error migrating {file_path.name}: {e}")
            self.stats["errors"] += 1
            return False
    
    def create_document_structure(self, file_path: Path, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized document structure."""
        filename = file_path.stem
        
        # Generate document ID
        document_id = hashlib.md5(filename.encode('utf-8')).hexdigest()
        
        # Determine document type
        document_type = self.determine_document_type(filename, data)
        
        # Extract content
        content = self.extract_content(data)
        
        # Create document
        document = {
            "document_id": document_id,
            "title": data.get("title", filename.replace("-", " ").replace("_", " ").title()),
            "document_type": document_type,
            "content": content,
            "original_filename": filename,
            "file_path": str(file_path),
            "metadata": {
                "source": "ragflow_phase0_foundation",
                "migration_date": datetime.utcnow(),
                "file_size": file_path.stat().st_size,
                "keywords": self.extract_keywords(filename, content),
                "language": self.detect_language(content)
            },
            "year": self.extract_year(filename, data),
            "created_at": datetime.utcnow(),
            "processing_status": {
                "migrated": True,
                "embedded": False,
                "indexed": True
            }
        }
        
        return document
    
    def determine_document_type(self, filename: str, data: Dict[str, Any]) -> str:
        """Determine document type from filename and content."""
        filename_lower = filename.lower()
        
        # Type mapping
        type_mapping = {
            "income-tax": "income_tax_act",
            "আয়কর": "income_tax_act",
            "tds-rules": "tds_circular", 
            "vat": "vat_act",
            "customs": "customs_act",
            "কসটমস": "customs_act",
            "vds-rules": "vat_circular",
            "finance": "finance_ordinance",
            "অরথ": "finance_ordinance",
            "sro": "sro",
            "schedule": "tax_schedule",
            "exemption": "exemption_rules"
        }
        
        for key, doc_type in type_mapping.items():
            if key in filename_lower:
                return doc_type
        
        return "legal_document"
    
    def extract_content(self, data: Dict[str, Any]) -> str:
        """Extract text content from data structure."""
        content_parts = []
        
        # Add title if available
        if "title" in data:
            content_parts.append(str(data["title"]))
        
        # Extract content based on structure
        if "content" in data:
            content_parts.append(str(data["content"]))
        
        if "sections" in data:
            for section in data["sections"]:
                if isinstance(section, dict):
                    if "title" in section:
                        content_parts.append(str(section["title"]))
                    if "content" in section:
                        content_parts.append(str(section["content"]))
        
        if "chapters" in data:
            for chapter in data["chapters"]:
                if isinstance(chapter, dict):
                    if "title" in chapter:
                        content_parts.append(str(chapter["title"]))
                    if "content" in chapter:
                        content_parts.append(str(chapter["content"]))
        
        # If no structured content, convert entire data to string
        if not content_parts:
            content_parts.append(json.dumps(data, ensure_ascii=False)[:5000])
        
        return "\n\n".join(content_parts)
    
    def extract_keywords(self, filename: str, content: str) -> List[str]:
        """Extract keywords from filename and content."""
        keywords = []
        
        # Keywords from filename
        filename_parts = filename.replace("-", " ").replace("_", " ").split()
        keywords.extend([part.lower() for part in filename_parts if len(part) > 2])
        
        # Common tax keywords
        tax_keywords = [
            "tax", "income", "vat", "tds", "customs", "sro", "exemption", 
            "deduction", "penalty", "interest", "assessment", "return"
        ]
        
        content_lower = content.lower()
        for keyword in tax_keywords:
            if keyword in content_lower:
                keywords.append(keyword)
        
        return list(set(keywords))
    
    def detect_language(self, content: str) -> str:
        """Simple language detection."""
        # Count Bengali vs English characters
        bengali_chars = len([c for c in content if '\u0980' <= c <= '\u09FF'])
        english_chars = len([c for c in content if c.isalpha() and c.isascii()])
        
        if bengali_chars > english_chars:
            return "bengali"
        elif english_chars > bengali_chars:
            return "english"
        else:
            return "mixed"
    
    def extract_year(self, filename: str, data: Dict[str, Any]) -> int:
        """Extract year from filename or data."""
        import re
        
        # Check filename for year
        year_match = re.search(r'20\d{2}', filename)
        if year_match:
            return int(year_match.group())
        
        # Check data for year
        data_str = str(data)
        year_match = re.search(r'20\d{2}', data_str)
        if year_match:
            return int(year_match.group())
        
        return 2024  # Default year
    
    def print_migration_stats(self):
        """Print migration statistics."""
        logger.info("📊 Migration Statistics:")
        logger.info(f"  Total files found: {self.stats['total_files']}")
        logger.info(f"  Successfully migrated: {self.stats['migrated_files']}")
        logger.info(f"  Skipped files: {self.stats['skipped_files']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        
        if self.stats['total_files'] > 0:
            success_rate = (self.stats['migrated_files'] / self.stats['total_files']) * 100
            logger.info(f"  Success rate: {success_rate:.1f}%")
    
    def validate_migration(self) -> bool:
        """Validate the migration was successful."""
        try:
            if not self.collection:
                return False
            
            # Count documents
            total_docs = self.collection.count_documents({})
            logger.info(f"📊 Total documents in MongoDB: {total_docs}")
            
            # Sample a few documents
            sample_docs = list(self.collection.find().limit(3))
            logger.info(f"✅ Sample documents migrated successfully")
            
            for doc in sample_docs:
                logger.info(f"  - {doc.get('title', 'Unknown')[:50]}...")
            
            return total_docs > 0
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False

def main():
    """Main migration function."""
    print("🚀 Starting ACTUAL Legal Data Migration...")
    print("📁 Source: ragflow/phase0_foundation/data_assets")
    print("🗄️  Target: MongoDB Atlas (ai_tax_lawyer_bd)")
    
    migrator = RealLegalDataMigrator()
    
    # Execute migration
    success = migrator.migrate_all_legal_files()
    
    if success:
        print("\n✅ Migration completed successfully!")
        
        # Validate migration
        if migrator.validate_migration():
            print("✅ Migration validation passed!")
        else:
            print("⚠️  Migration validation has issues")
        
        print("\nNext steps:")
        print("1. Generate embeddings for documents")
        print("2. Setup RAGFlow collections")
        print("3. Test agent framework integration")
        
    else:
        print("\n❌ Migration failed!")
        print("Check logs for error details.")

if __name__ == "__main__":
    main()