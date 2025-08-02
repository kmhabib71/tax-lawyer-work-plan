#!/usr/bin/env python3
"""
Legal data seeder for migrating 1,524 legal files to MongoDB.
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import sys
import os
import re

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings
from utils.logging_utils import setup_logging, log_database_operation
import openai

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class LegalDataSeeder:
    """Handles migration of 1,524 legal files to MongoDB."""
    
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.database = self.client[settings.mongodb_database]
        self.collection = self.database["legal_documents"]
        
        # Setup OpenAI for embeddings
        openai.api_key = settings.openai_api_key
        
        # Legal file paths
        self.legal_files_base = Path("/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap")
        self.structured_laws_path = self.legal_files_base / "precise_structured_laws"
        self.fixed_laws_path = self.legal_files_base / "fixed_structured_laws"
        self.circulars_path = self.legal_files_base / "income-tax-complete-circular-24-25"
        
        # Document type mappings
        self.document_type_mapping = {
            "অর্থ_আইন": "income_tax_act",
            "কাস্টমস_আইন": "customs_act", 
            "আয়কর_অধ্যাদেশ": "income_tax_act",
            "ভ্যাট_আইন": "vat_act",
            "Income_Tax": "income_tax_act",
            "circular": "tds_circular",
            "tds": "tds_circular",
            "sro": "sro",
            "form": "form_template"
        }
    
    async def migrate_all_legal_files(self) -> bool:
        """Migrate all 1,524 legal files to MongoDB."""
        try:
            logger.info("🚀 Starting legal data migration...")
            
            # Step 1: Migrate structured laws
            await self.migrate_structured_laws()
            
            # Step 2: Migrate fixed structured laws
            await self.migrate_fixed_laws()
            
            # Step 3: Migrate circulars and TDS documents
            await self.migrate_circulars()
            
            # Step 4: Generate embeddings for all documents
            await self.generate_embeddings()
            
            # Step 5: Validate migration
            await self.validate_migration()
            
            logger.info("✅ Legal data migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Legal data migration failed: {e}")
            return False
        finally:
            await self.client.close()
    
    async def migrate_structured_laws(self):
        """Migrate structured laws from precise_structured_laws directory."""
        logger.info("Migrating structured laws...")
        
        structured_files = list(self.structured_laws_path.glob("*.json"))
        logger.info(f"Found {len(structured_files)} structured law files")
        
        migrated_count = 0
        for file_path in structured_files:
            try:
                if await self.migrate_structured_law_file(file_path):
                    migrated_count += 1
                    
                if migrated_count % 10 == 0:
                    logger.info(f"Migrated {migrated_count}/{len(structured_files)} structured laws")
                    
            except Exception as e:
                logger.error(f"Error migrating {file_path}: {e}")
        
        logger.info(f"✅ Migrated {migrated_count} structured law files")
    
    async def migrate_structured_law_file(self, file_path: Path) -> bool:
        """Migrate a single structured law file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract document metadata
            filename = file_path.stem
            document_type = self.determine_document_type(filename, data)
            
            # Create document structure
            document = {
                "document_id": self.generate_document_id(filename),
                "title": data.get("title", filename),
                "title_english": self.extract_english_title(data),
                "document_type": document_type,
                "content": self.extract_full_content(data),
                "content_english": data.get("content_english"),
                "sections": self.extract_sections(data),
                "metadata": {
                    "act_reference": data.get("act_reference"),
                    "effective_date": self.parse_date(data.get("effective_date")),
                    "amendment_date": self.parse_date(data.get("amendment_date")),
                    "status": "active",
                    "keywords": self.extract_keywords(data),
                    "tags": self.generate_tags(document_type, data)
                },
                "year": self.extract_year(data, filename),
                "language": self.determine_language(data),
                "source": {
                    "original_file_path": str(file_path),
                    "extraction_method": "manual",
                    "quality_score": self.assess_quality(data)
                },
                "processing": {
                    "chunked": False,
                    "embedded": False,
                    "indexed": True,
                    "last_processed": datetime.utcnow(),
                    "processing_version": "1.0"
                },
                "usage_stats": {
                    "query_count": 0,
                    "relevance_score": 0.0,
                    "last_accessed": None
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "version": "1.0"
            }
            
            # Check if document already exists
            existing = await self.collection.find_one({"document_id": document["document_id"]})
            if existing:
                logger.debug(f"Document {document['document_id']} already exists")
                return False
            
            # Insert document
            start_time = datetime.utcnow()
            await self.collection.insert_one(document)
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            log_database_operation("insert", "legal_documents", duration_ms, True)
            logger.debug(f"Migrated: {document['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Error migrating {file_path}: {e}")
            return False
    
    async def migrate_fixed_laws(self):
        """Migrate fixed structured laws."""
        logger.info("Migrating fixed structured laws...")
        
        fixed_files = list(self.fixed_laws_path.glob("*.json"))
        logger.info(f"Found {len(fixed_files)} fixed law files")
        
        migrated_count = 0
        for file_path in fixed_files:
            try:
                if await self.migrate_structured_law_file(file_path):
                    migrated_count += 1
            except Exception as e:
                logger.error(f"Error migrating {file_path}: {e}")
        
        logger.info(f"✅ Migrated {migrated_count} fixed law files")
    
    async def migrate_circulars(self):
        """Migrate circular and TDS documents."""
        logger.info("Migrating circulars and TDS documents...")
        
        # Find all markdown files in circulars directory
        circular_files = []
        for pattern in ["**/*.md", "**/*.txt", "**/*.html"]:
            circular_files.extend(self.circulars_path.glob(pattern))
        
        logger.info(f"Found {len(circular_files)} circular files")
        
        migrated_count = 0
        for file_path in circular_files:
            try:
                if await self.migrate_circular_file(file_path):
                    migrated_count += 1
                    
                if migrated_count % 20 == 0:
                    logger.info(f"Migrated {migrated_count}/{len(circular_files)} circular files")
                    
            except Exception as e:
                logger.error(f"Error migrating {file_path}: {e}")
        
        logger.info(f"✅ Migrated {migrated_count} circular files")
    
    async def migrate_circular_file(self, file_path: Path) -> bool:
        """Migrate a single circular file."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content.strip()) < 100:  # Skip very short files
                return False
            
            # Extract metadata from path and content
            filename = file_path.stem
            document_type = self.determine_circular_type(file_path, content)
            
            # Create document structure
            document = {
                "document_id": self.generate_document_id(f"circular_{filename}"),
                "title": self.extract_circular_title(content, filename),
                "document_type": document_type,
                "content": content,
                "sections": self.extract_circular_sections(content),
                "metadata": {
                    "status": "active",
                    "keywords": self.extract_circular_keywords(content),
                    "tags": self.generate_circular_tags(file_path)
                },
                "year": self.extract_circular_year(file_path, content),
                "language": "english" if self.is_english_content(content) else "bengali",
                "source": {
                    "original_file_path": str(file_path),
                    "extraction_method": "manual",
                    "quality_score": 0.8
                },
                "processing": {
                    "chunked": False,
                    "embedded": False,
                    "indexed": True,
                    "last_processed": datetime.utcnow(),
                    "processing_version": "1.0"
                },
                "usage_stats": {
                    "query_count": 0,
                    "relevance_score": 0.0,
                    "last_accessed": None
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "version": "1.0"
            }
            
            # Check if document already exists
            existing = await self.collection.find_one({"document_id": document["document_id"]})
            if existing:
                return False
            
            # Insert document
            start_time = datetime.utcnow()
            await self.collection.insert_one(document)
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            log_database_operation("insert", "legal_documents", duration_ms, True)
            return True
            
        except Exception as e:
            logger.error(f"Error migrating circular {file_path}: {e}")
            return False
    
    async def generate_embeddings(self):
        """Generate embeddings for all documents."""
        logger.info("Generating embeddings for all documents...")
        
        # Find documents without embeddings
        cursor = self.collection.find({"processing.embedded": False})
        documents = await cursor.to_list(length=None)
        
        logger.info(f"Generating embeddings for {len(documents)} documents")
        
        embedded_count = 0
        for doc in documents:
            try:
                if await self.generate_document_embedding(doc):
                    embedded_count += 1
                    
                if embedded_count % 10 == 0:
                    logger.info(f"Generated embeddings for {embedded_count}/{len(documents)} documents")
                    
            except Exception as e:
                logger.error(f"Error generating embedding for {doc['document_id']}: {e}")
        
        logger.info(f"✅ Generated {embedded_count} embeddings")
    
    async def generate_document_embedding(self, document: Dict[str, Any]) -> bool:
        """Generate embedding for a single document."""
        try:
            # Prepare text for embedding
            embedding_text = self.prepare_embedding_text(document)
            
            # Generate embedding using OpenAI
            response = await openai.Embedding.acreate(
                model=settings.openai_embedding_model,
                input=embedding_text
            )
            
            embedding = response['data'][0]['embedding']
            
            # Update document with embedding
            start_time = datetime.utcnow()
            await self.collection.update_one(
                {"_id": document["_id"]},
                {
                    "$set": {
                        "content_embedding": embedding,
                        "processing.embedded": True,
                        "processing.last_processed": datetime.utcnow()
                    }
                }
            )
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            log_database_operation("update", "legal_documents", duration_ms, True)
            return True
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return False
    
    def prepare_embedding_text(self, document: Dict[str, Any]) -> str:
        """Prepare text for embedding generation."""
        parts = []
        
        # Add title
        if document.get("title"):
            parts.append(document["title"])
        
        # Add content (truncated if too long)
        content = document.get("content", "")
        if len(content) > 8000:  # OpenAI token limit consideration
            content = content[:8000] + "..."
        parts.append(content)
        
        # Add keywords
        keywords = document.get("metadata", {}).get("keywords", [])
        if keywords:
            parts.append(" ".join(keywords))
        
        return "\n\n".join(parts)
    
    async def validate_migration(self):
        """Validate the migration results."""
        try:
            # Count documents by type
            document_counts = {}
            for doc_type in self.document_type_mapping.values():
                count = await self.collection.count_documents({"document_type": doc_type})
                document_counts[doc_type] = count
            
            total_documents = await self.collection.count_documents({})
            embedded_documents = await self.collection.count_documents({"processing.embedded": True})
            
            logger.info("📊 Migration Validation Results:")
            logger.info(f"  Total documents: {total_documents}")
            logger.info(f"  Embedded documents: {embedded_documents}")
            logger.info(f"  Document types:")
            
            for doc_type, count in document_counts.items():
                logger.info(f"    {doc_type}: {count}")
            
            # Validate sample documents
            sample_doc = await self.collection.find_one({"processing.embedded": True})
            if sample_doc:
                logger.info(f"✅ Sample document validation passed")
                logger.info(f"  Document ID: {sample_doc['document_id']}")
                logger.info(f"  Title: {sample_doc['title'][:50]}...")
                logger.info(f"  Embedding dimensions: {len(sample_doc.get('content_embedding', []))}")
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
    
    # Helper methods for data extraction and processing
    
    def generate_document_id(self, filename: str) -> str:
        """Generate unique document ID."""
        return hashlib.md5(filename.encode('utf-8')).hexdigest()
    
    def determine_document_type(self, filename: str, data: Dict[str, Any]) -> str:
        """Determine document type from filename and content."""
        for key, doc_type in self.document_type_mapping.items():
            if key in filename.lower():
                return doc_type
        
        # Check content for clues
        content = str(data).lower()
        if "income tax" in content or "আয়কর" in content:
            return "income_tax_act"
        elif "vat" in content or "ভ্যাট" in content:
            return "vat_act"
        elif "customs" in content or "কাস্টমস" in content:
            return "customs_act"
        
        return "guideline"
    
    def determine_circular_type(self, file_path: Path, content: str) -> str:
        """Determine circular document type."""
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        if "tds" in path_str or "tds" in content_lower:
            return "tds_circular"
        elif "sro" in path_str or "sro" in content_lower:
            return "sro"
        elif "form" in path_str:
            return "form_template"
        else:
            return "guideline"
    
    def extract_sections(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sections from structured data."""
        sections = []
        
        if isinstance(data, dict):
            if "chapters" in data:
                for chapter in data["chapters"]:
                    if isinstance(chapter, dict):
                        section = {
                            "section_number": chapter.get("chapter", ""),
                            "section_title": chapter.get("title", ""),
                            "section_content": chapter.get("content", ""),
                            "subsections": []
                        }
                        
                        if "sections" in chapter:
                            for subsection in chapter["sections"]:
                                if isinstance(subsection, dict):
                                    section["subsections"].append({
                                        "subsection_number": subsection.get("section", ""),
                                        "subsection_content": subsection.get("content", "")
                                    })
                        
                        sections.append(section)
        
        return sections
    
    def extract_full_content(self, data: Dict[str, Any]) -> str:
        """Extract full text content from structured data."""
        content_parts = []
        
        if isinstance(data, dict):
            # Add title
            if "title" in data:
                content_parts.append(data["title"])
            
            # Add chapters content
            if "chapters" in data:
                for chapter in data["chapters"]:
                    if isinstance(chapter, dict):
                        if "title" in chapter:
                            content_parts.append(chapter["title"])
                        if "content" in chapter:
                            content_parts.append(chapter["content"])
                        
                        if "sections" in chapter:
                            for section in chapter["sections"]:
                                if isinstance(section, dict) and "content" in section:
                                    content_parts.append(section["content"])
            
            # Add direct content
            if "content" in data:
                content_parts.append(str(data["content"]))
        
        return "\n\n".join(content_parts)
    
    def extract_keywords(self, data: Dict[str, Any]) -> List[str]:
        """Extract keywords from data."""
        keywords = []
        content = str(data).lower()
        
        # Common tax keywords
        tax_keywords = [
            "tax", "income", "salary", "rebate", "exemption", "deduction",
            "tds", "vat", "customs", "penalty", "interest", "assessment"
        ]
        
        for keyword in tax_keywords:
            if keyword in content:
                keywords.append(keyword)
        
        return keywords
    
    def generate_tags(self, document_type: str, data: Dict[str, Any]) -> List[str]:
        """Generate tags for categorization."""
        tags = [document_type]
        
        # Add year tag if available
        year = self.extract_year(data, "")
        if year:
            tags.append(f"year_{year}")
        
        # Add language tag
        language = self.determine_language(data)
        tags.append(language)
        
        return tags
    
    def extract_year(self, data: Dict[str, Any], filename: str) -> Optional[int]:
        """Extract year from data or filename."""
        # Check filename for year
        year_match = re.search(r'20\d{2}', filename)
        if year_match:
            return int(year_match.group())
        
        # Check data content
        content = str(data)
        year_match = re.search(r'20\d{2}', content)
        if year_match:
            return int(year_match.group())
        
        return 2024  # Default year
    
    def determine_language(self, data: Dict[str, Any]) -> str:
        """Determine document language."""
        content = str(data)
        
        # Simple heuristic for Bengali detection
        bengali_chars = len(re.findall(r'[\u0980-\u09FF]', content))
        english_chars = len(re.findall(r'[a-zA-Z]', content))
        
        if bengali_chars > english_chars:
            return "bengali"
        elif english_chars > bengali_chars:
            return "english"
        else:
            return "bilingual"
    
    def extract_english_title(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract English title if available."""
        if isinstance(data, dict):
            return data.get("title_english") or data.get("english_title")
        return None
    
    def parse_date(self, date_str: Any) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None
        
        try:
            if isinstance(date_str, str):
                # Try common date formats
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y"]:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
        except:
            pass
        
        return None
    
    def assess_quality(self, data: Dict[str, Any]) -> float:
        """Assess document quality score."""
        score = 0.5  # Base score
        
        if isinstance(data, dict):
            if "title" in data:
                score += 0.1
            if "chapters" in data:
                score += 0.2
            if "content" in data and len(str(data["content"])) > 100:
                score += 0.2
        
        return min(score, 1.0)
    
    def extract_circular_title(self, content: str, filename: str) -> str:
        """Extract title from circular content."""
        lines = content.split('\n')
        
        # Look for title in first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 10 and not line.startswith('#'):
                return line[:100]
        
        return filename.replace('_', ' ').title()
    
    def extract_circular_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract sections from circular content."""
        sections = []
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            # Check if line is a header
            if line.startswith('#') or line.strip().isupper():
                if current_section:
                    current_section["section_content"] = '\n'.join(current_content)
                    sections.append(current_section)
                
                current_section = {
                    "section_number": str(len(sections) + 1),
                    "section_title": line.strip('#').strip(),
                    "section_content": "",
                    "subsections": []
                }
                current_content = []
            else:
                current_content.append(line)
        
        # Add last section
        if current_section:
            current_section["section_content"] = '\n'.join(current_content)
            sections.append(current_section)
        
        return sections
    
    def extract_circular_keywords(self, content: str) -> List[str]:
        """Extract keywords from circular content."""
        keywords = []
        content_lower = content.lower()
        
        circular_keywords = [
            "circular", "tds", "withholding", "tax", "rate", "deadline",
            "form", "return", "submission", "penalty", "interest"
        ]
        
        for keyword in circular_keywords:
            if keyword in content_lower:
                keywords.append(keyword)
        
        return keywords
    
    def generate_circular_tags(self, file_path: Path) -> List[str]:
        """Generate tags for circular documents."""
        tags = []
        path_str = str(file_path).lower()
        
        if "tds" in path_str:
            tags.append("tds")
        if "24-25" in path_str:
            tags.append("year_2024")
        if "25-26" in path_str:
            tags.append("year_2025")
        
        tags.append("circular")
        return tags
    
    def extract_circular_year(self, file_path: Path, content: str) -> int:
        """Extract year from circular path or content."""
        path_str = str(file_path)
        
        # Check for year patterns
        if "24-25" in path_str:
            return 2024
        elif "25-26" in path_str:
            return 2025
        
        # Check content
        year_match = re.search(r'20\d{2}', content)
        if year_match:
            return int(year_match.group())
        
        return 2024
    
    def is_english_content(self, content: str) -> bool:
        """Check if content is primarily English."""
        english_chars = len(re.findall(r'[a-zA-Z]', content))
        bengali_chars = len(re.findall(r'[\u0980-\u09FF]', content))
        
        return english_chars > bengali_chars

async def main():
    """Main seeder function."""
    print("🚀 Starting legal data migration...")
    
    seeder = LegalDataSeeder()
    success = await seeder.migrate_all_legal_files()
    
    if success:
        print("✅ Legal data migration completed successfully!")
        print("\nNext steps:")
        print("1. Configure RAGFlow collections")
        print("2. Create vector embeddings")
        print("3. Test knowledge retrieval")
    else:
        print("❌ Legal data migration failed!")
        print("Check logs for error details.")

if __name__ == "__main__":
    asyncio.run(main())