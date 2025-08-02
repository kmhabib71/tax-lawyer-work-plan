#!/usr/bin/env python3
"""
Complete Dataset Migration - Week 1 Foundation
Migrate all available legal documents to MongoDB for senior lawyer foundation
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import pymongo
from urllib.parse import quote_plus

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteLegalDataMigrator:
    """
    Complete migration of all legal documents for Week 1 foundation
    """
    
    def __init__(self):
        self.connection_string = "mongodb+srv://habib:Khurshida71@cluster0.qqlnw.mongodb.net/ai-tax-lawyer?retryWrites=true&w=majority&appName=Cluster0"
        self.database_name = "ai_tax_lawyer_bd"
        self.collection_name = "legal_documents_complete"
        self.client = None
        self.db = None
        self.collection = None
        
        # Document categories for organization
        self.categories = {
            'income_tax': ['income', 'আয়কর', 'salary', 'exemption'],
            'corporate_tax': ['corporate', 'company', 'business'],
            'vat_customs': ['vat', 'customs', 'কাস্টমস', 'ভ্যাট'],
            'finance_ordinance': ['finance', 'ordinance', 'অর্থ', 'অধ্যাদেশ'],
            'circulars': ['circular', 'sro', 'notification'],
            'schedules': ['schedule', 'তফসিল', 'part'],
            'forms': ['form', 'ereturn', 'validation'],
            'other': []
        }
    
    def connect_database(self) -> bool:
        """Connect to MongoDB"""
        try:
            self.client = pymongo.MongoClient(self.connection_string)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            logger.info(f"✅ Connected to MongoDB: {self.database_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def find_all_legal_files(self) -> List[Path]:
        """Find all legal JSON files in the project"""
        logger.info("🔍 Scanning for all legal JSON files...")
        
        # Search patterns for legal files
        search_patterns = [
            "**/*income*tax*.json",
            "**/*আয়কর*.json",
            "**/*finance*.json",
            "**/*অর্থ*.json", 
            "**/*vat*.json",
            "**/*customs*.json",
            "**/*কাস্টমস*.json",
            "**/*legal*.json",
            "**/*tax*.json",
            "**/*law*.json",
            "**/*act*.json",
            "**/*ordinance*.json",
            "**/*schedule*.json",
            "**/*circular*.json",
            "**/*sro*.json"
        ]
        
        all_files = set()
        base_path = Path("/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap")
        
        for pattern in search_patterns:
            files = list(base_path.glob(pattern))
            all_files.update(files)
            logger.info(f"   Pattern '{pattern}': {len(files)} files")
        
        # Filter out system files
        legal_files = []
        for file in all_files:
            # Skip system directories
            if any(exclude in str(file) for exclude in ['.vscode', '.claude', 'node_modules', '__pycache__']):
                continue
            
            # Check if file contains legal content
            if self._is_legal_file(file):
                legal_files.append(file)
        
        logger.info(f"✅ Found {len(legal_files)} legal files for migration")
        return legal_files
    
    def _is_legal_file(self, file_path: Path) -> bool:
        """Check if file contains legal content"""
        try:
            if file_path.stat().st_size > 100 * 1024 * 1024:  # Skip files > 100MB
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read first 1000 characters to check content
                sample = f.read(1000).lower()
                
                # Legal content indicators
                legal_indicators = [
                    'tax', 'আয়কর', 'অর্থ', 'আইন', 'ধারা', 'section', 'act', 'law',
                    'ordinance', 'schedule', 'vat', 'customs', 'sro', 'circular',
                    'exemption', 'deduction', 'penalty', 'assessment', 'return'
                ]
                
                return any(indicator in sample for indicator in legal_indicators)
                
        except Exception:
            return False
    
    def categorize_document(self, file_path: Path, content: Dict) -> str:
        """Categorize document based on filename and content"""
        file_str = str(file_path).lower()
        content_str = str(content).lower()
        
        for category, keywords in self.categories.items():
            if category == 'other':
                continue
            
            if any(keyword in file_str or keyword in content_str for keyword in keywords):
                return category
        
        return 'other'
    
    def extract_metadata(self, file_path: Path, content: Dict) -> Dict[str, Any]:
        """Extract comprehensive metadata from document"""
        metadata = {
            'source_file': str(file_path),
            'filename': file_path.name,
            'file_size': file_path.stat().st_size,
            'category': self.categorize_document(file_path, content),
            'language': 'mixed',  # Most Bangladesh legal docs are mixed Bengali/English
            'processed_at': datetime.now(),
            'content_length': len(str(content)),
            'estimated_tokens': len(str(content).split()),
        }
        
        # Extract specific legal metadata
        if isinstance(content, dict):
            # Common legal document fields
            legal_fields = {
                'act_name': ['act_name', 'title', 'name'],
                'section': ['section', 'ধারা', 'clause'],
                'year': ['year', 'সাল', 'date'],
                'type': ['type', 'document_type', 'category'],
                'authority': ['authority', 'ministry', 'department']
            }
            
            for meta_key, field_names in legal_fields.items():
                for field_name in field_names:
                    if field_name in content:
                        metadata[meta_key] = content[field_name]
                        break
        
        return metadata
    
    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process single document for migration"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # Create standardized document structure
            document = {
                'document_id': f"legal_{hash(str(file_path))}",
                'metadata': self.extract_metadata(file_path, content),
                'original_content': content,
                'searchable_text': self._extract_searchable_text(content),
                'indexed_keywords': self._extract_keywords(content),
                'migration_batch': 'week1_complete',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            return document
            
        except Exception as e:
            logger.error(f"❌ Failed to process {file_path}: {e}")
            return None
    
    def _extract_searchable_text(self, content: Any) -> str:
        """Extract all searchable text from content"""
        text_parts = []
        
        def extract_text_recursive(obj):
            if isinstance(obj, str):
                if len(obj) > 10:  # Only meaningful text
                    text_parts.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_text_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text_recursive(item)
        
        extract_text_recursive(content)
        return ' '.join(text_parts)
    
    def _extract_keywords(self, content: Any) -> List[str]:
        """Extract important keywords for indexing"""
        text = str(content).lower()
        
        # Important legal keywords
        legal_keywords = [
            'আয়কর', 'income tax', 'অর্থ', 'finance', 'ভ্যাট', 'vat', 
            'কাস্টমস', 'customs', 'ছাড়', 'exemption', 'কর', 'tax',
            'ধারা', 'section', 'তফসিল', 'schedule', 'আইন', 'act',
            'অধ্যাদেশ', 'ordinance', 'নিয়ম', 'rule', 'বিধি', 'regulation'
        ]
        
        found_keywords = []
        for keyword in legal_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def migrate_all_documents(self) -> Dict[str, Any]:
        """Migrate all found legal documents"""
        if not self.connect_database():
            return {'success': False, 'error': 'Database connection failed'}
        
        # Find all legal files
        legal_files = self.find_all_legal_files()
        
        if not legal_files:
            return {'success': False, 'error': 'No legal files found'}
        
        # Migration statistics
        stats = {
            'total_files': len(legal_files),
            'processed': 0,
            'failed': 0,
            'categories': {},
            'start_time': datetime.now()
        }
        
        logger.info(f"🚀 Starting migration of {len(legal_files)} legal documents...")
        
        # Process files in batches
        batch_size = 50
        for i in range(0, len(legal_files), batch_size):
            batch_files = legal_files[i:i + batch_size]
            batch_documents = []
            
            logger.info(f"📦 Processing batch {i//batch_size + 1}/{(len(legal_files) + batch_size - 1)//batch_size}")
            
            for file_path in batch_files:
                document = self.process_document(file_path)
                if document:
                    batch_documents.append(document)
                    stats['processed'] += 1
                    
                    # Track categories
                    category = document['metadata']['category']
                    stats['categories'][category] = stats['categories'].get(category, 0) + 1
                else:
                    stats['failed'] += 1
            
            # Insert batch to database
            if batch_documents:
                try:
                    result = self.collection.insert_many(batch_documents, ordered=False)
                    logger.info(f"   ✅ Inserted {len(result.inserted_ids)} documents")
                except Exception as e:
                    logger.error(f"   ❌ Batch insert failed: {e}")
                    stats['failed'] += len(batch_documents)
        
        # Create indexes for performance
        self._create_indexes()
        
        stats['end_time'] = datetime.now()
        stats['duration'] = str(stats['end_time'] - stats['start_time'])
        
        return {
            'success': True,
            'statistics': stats,
            'database': self.database_name,
            'collection': self.collection_name
        }
    
    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        logger.info("📊 Creating database indexes...")
        
        try:
            # Text search index
            self.collection.create_index([
                ("searchable_text", "text"),
                ("metadata.act_name", "text"),
                ("indexed_keywords", "text")
            ], name="legal_text_search")
            
            # Category and metadata indexes
            self.collection.create_index("metadata.category")
            self.collection.create_index("metadata.year")
            self.collection.create_index("metadata.type")
            self.collection.create_index("created_at")
            
            # Compound indexes for complex queries
            self.collection.create_index([
                ("metadata.category", 1),
                ("metadata.year", -1)
            ], name="category_year_index")
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {e}")

def main():
    """Run complete dataset migration"""
    print("🏗️ Week 1 Foundation: Complete Legal Dataset Migration")
    print("="*60)
    
    migrator = CompleteLegalDataMigrator()
    result = migrator.migrate_all_documents()
    
    if result['success']:
        stats = result['statistics']
        print(f"\n✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print(f"📊 Statistics:")
        print(f"   Total files found: {stats['total_files']}")
        print(f"   Successfully processed: {stats['processed']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Duration: {stats['duration']}")
        print(f"\n📂 Document Categories:")
        for category, count in stats['categories'].items():
            print(f"   {category}: {count} documents")
        
        print(f"\n🗄️ Database: {result['database']}")
        print(f"📦 Collection: {result['collection']}")
        print(f"\n🎯 Week 1 Foundation: Legal dataset migration complete!")
        
    else:
        print(f"❌ Migration failed: {result['error']}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)