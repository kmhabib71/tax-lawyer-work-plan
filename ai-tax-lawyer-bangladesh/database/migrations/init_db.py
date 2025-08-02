#!/usr/bin/env python3
"""
Database initialization script for AI Tax Lawyer Bangladesh.
Creates collections, indexes, and seeds initial data.
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from config.settings import settings
from database.indexes.vector_indexes import create_all_indexes
from utils.logging_utils import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Handles database initialization and setup."""
    
    def __init__(self):
        self.sync_client = MongoClient(settings.mongodb_url)
        self.async_client = AsyncIOMotorClient(settings.mongodb_url)
        self.database = self.async_client[settings.mongodb_database]
        self.sync_database = self.sync_client[settings.mongodb_database]
    
    async def initialize_database(self) -> bool:
        """Initialize the complete database setup."""
        try:
            logger.info("Starting database initialization...")
            
            # Step 1: Create collections
            await self.create_collections()
            
            # Step 2: Create indexes (sync operation)
            self.create_indexes()
            
            # Step 3: Seed initial data
            await self.seed_initial_data()
            
            # Step 4: Validate setup
            await self.validate_setup()
            
            logger.info("✅ Database initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
        finally:
            self.sync_client.close()
            self.async_client.close()
    
    async def create_collections(self):
        """Create all required collections with validation schemas."""
        collections = {
            "legal_documents": "legal_documents.json",
            "document_embeddings": "document_embeddings.json", 
            "tax_rules": "tax_rules.json",
            "tax_slabs": "tax_slabs.json",
            "exemptions_rebates": "exemptions_rebates.json",
            "user_sessions": "user_sessions.json",
            "calculation_history": "tax_calculations.json",
            "agent_logs": "agent_logs.json",
            "agent_cache": "agent_cache.json",
            "form_templates": "form_templates.json",
            "compliance_tracking": "compliance_tracking.json",
            "legal_precedents": "legal_precedents.json"
        }
        
        for collection_name, schema_file in collections.items():
            await self.create_collection_with_schema(collection_name, schema_file)
    
    async def create_collection_with_schema(self, collection_name: str, schema_file: str):
        """Create a collection with JSON schema validation."""
        try:
            # Check if collection exists
            existing_collections = await self.database.list_collection_names()
            
            if collection_name in existing_collections:
                logger.info(f"Collection {collection_name} already exists")
                return
            
            # Load schema if exists
            schema_path = project_root / "database" / "schemas" / schema_file
            
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                
                # Create collection with schema validation
                await self.database.create_collection(
                    collection_name,
                    validator=schema
                )
                logger.info(f"✅ Created collection {collection_name} with schema validation")
            else:
                # Create collection without schema
                await self.database.create_collection(collection_name)
                logger.info(f"✅ Created collection {collection_name} (no schema)")
                
        except Exception as e:
            logger.error(f"❌ Error creating collection {collection_name}: {e}")
    
    def create_indexes(self):
        """Create all database indexes."""
        try:
            logger.info("Creating database indexes...")
            success = create_all_indexes(self.sync_client)
            
            if success:
                logger.info("✅ All indexes created successfully")
            else:
                logger.warning("⚠️  Some indexes failed to create")
                
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
    
    async def seed_initial_data(self):
        """Seed initial data into collections."""
        try:
            logger.info("Seeding initial data...")
            
            # Seed tax slabs
            await self.seed_tax_slabs()
            
            # Seed tax rules
            await self.seed_tax_rules()
            
            # Seed exemptions and rebates
            await self.seed_exemptions_rebates()
            
            # Seed form templates
            await self.seed_form_templates()
            
            logger.info("✅ Initial data seeded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error seeding initial data: {e}")
    
    async def seed_tax_slabs(self):
        """Seed tax slab data."""
        tax_slabs = [
            {
                "slab_id": "income_tax_2024",
                "tax_type": "income_tax",
                "year": 2024,
                "applicable_to": "individual",
                "slabs": [
                    {"min_income": 0, "max_income": 350000, "tax_rate": 0.0, "description": "Tax-free"},
                    {"min_income": 350000, "max_income": 450000, "tax_rate": 0.05, "description": "5%"},
                    {"min_income": 450000, "max_income": 750000, "tax_rate": 0.10, "description": "10%"},
                    {"min_income": 750000, "max_income": 1150000, "tax_rate": 0.15, "description": "15%"},
                    {"min_income": 1150000, "max_income": 1650000, "tax_rate": 0.20, "description": "20%"},
                    {"min_income": 1650000, "max_income": float('inf'), "tax_rate": 0.25, "description": "25%"}
                ],
                "created_at": datetime.utcnow(),
                "status": "active"
            },
            {
                "slab_id": "corporate_tax_2024",
                "tax_type": "corporate_tax",
                "year": 2024,
                "applicable_to": "company",
                "slabs": [
                    {"min_income": 0, "max_income": float('inf'), "tax_rate": 0.225, "description": "22.5% for companies"}
                ],
                "created_at": datetime.utcnow(),
                "status": "active"
            }
        ]
        
        collection = self.database["tax_slabs"]
        for slab in tax_slabs:
            existing = await collection.find_one({"slab_id": slab["slab_id"]})
            if not existing:
                await collection.insert_one(slab)
                logger.info(f"Seeded tax slab: {slab['slab_id']}")
    
    async def seed_tax_rules(self):
        """Seed basic tax rules."""
        tax_rules = [
            {
                "rule_id": "basic_exemption_2024",
                "rule_name": "Basic Exemption Limit",
                "rule_type": "exemption",
                "description": "Basic tax-free income limit for individuals",
                "formula": "min_exemption = 350000",
                "parameters": {
                    "exemption_amount": 350000,
                    "applicable_year": 2024,
                    "currency": "BDT"
                },
                "conditions": [
                    "applies to individual taxpayers",
                    "resident status required"
                ],
                "legal_reference": "Income Tax Act 2023, Section 44",
                "created_at": datetime.utcnow(),
                "status": "active"
            },
            {
                "rule_id": "investment_rebate_2024",
                "rule_name": "Investment Rebate Calculation",
                "rule_type": "rebate",
                "description": "Rebate for approved investments",
                "formula": "rebate = min(investment_amount * 0.15, total_tax * 0.3)",
                "parameters": {
                    "rebate_rate": 0.15,
                    "max_rebate_percentage": 0.3,
                    "applicable_year": 2024
                },
                "conditions": [
                    "investment in approved securities",
                    "minimum investment period 5 years"
                ],
                "legal_reference": "Income Tax Act 2023, Section 44BA",
                "created_at": datetime.utcnow(),
                "status": "active"
            }
        ]
        
        collection = self.database["tax_rules"]
        for rule in tax_rules:
            existing = await collection.find_one({"rule_id": rule["rule_id"]})
            if not existing:
                await collection.insert_one(rule)
                logger.info(f"Seeded tax rule: {rule['rule_id']}")
    
    async def seed_exemptions_rebates(self):
        """Seed exemptions and rebates data."""
        exemptions = [
            {
                "exemption_id": "house_rent_allowance",
                "exemption_name": "House Rent Allowance",
                "exemption_type": "salary_exemption",
                "description": "Exemption for house rent allowance up to specified limits",
                "calculation_method": "min(actual_allowance, 25% * basic_salary, max_limit)",
                "parameters": {
                    "max_percentage": 0.25,
                    "max_limit_dhaka": 300000,
                    "max_limit_other": 150000
                },
                "conditions": [
                    "must be actual house rent allowance",
                    "location-based limits apply"
                ],
                "legal_reference": "Income Tax Act 2023, Section 10(10)",
                "year": 2024,
                "created_at": datetime.utcnow(),
                "status": "active"
            },
            {
                "exemption_id": "provident_fund",
                "exemption_name": "Provident Fund Contribution",
                "exemption_type": "investment_exemption",
                "description": "Exemption for provident fund contributions",
                "calculation_method": "recognized_pf_contribution",
                "parameters": {
                    "max_exemption": 500000,
                    "employer_contribution_limit": "no_limit"
                },
                "conditions": [
                    "must be recognized provident fund",
                    "employer and employee contributions"
                ],
                "legal_reference": "Income Tax Act 2023, Section 10(11)",
                "year": 2024,
                "created_at": datetime.utcnow(),
                "status": "active"
            }
        ]
        
        collection = self.database["exemptions_rebates"]
        for exemption in exemptions:
            existing = await collection.find_one({"exemption_id": exemption["exemption_id"]})
            if not existing:
                await collection.insert_one(exemption)
                logger.info(f"Seeded exemption: {exemption['exemption_id']}")
    
    async def seed_form_templates(self):
        """Seed form templates."""
        forms = [
            {
                "form_id": "ereturn_individual_2024",
                "form_name": "Individual Income Tax Return",
                "form_type": "ereturn",
                "version": "2024.1",
                "year": 2024,
                "description": "Standard individual income tax return form",
                "sections": [
                    {
                        "section_id": "personal_info",
                        "section_name": "Personal Information",
                        "fields": [
                            {"field_id": "tin", "field_name": "TIN", "field_type": "string", "required": True},
                            {"field_id": "name", "field_name": "Full Name", "field_type": "string", "required": True},
                            {"field_id": "father_name", "field_name": "Father's Name", "field_type": "string", "required": True},
                            {"field_id": "mother_name", "field_name": "Mother's Name", "field_type": "string", "required": True},
                            {"field_id": "spouse_name", "field_name": "Spouse Name", "field_type": "string", "required": False}
                        ]
                    },
                    {
                        "section_id": "income_details",
                        "section_name": "Income Details",
                        "fields": [
                            {"field_id": "salary_income", "field_name": "Salary Income", "field_type": "number", "required": True},
                            {"field_id": "house_rent_allowance", "field_name": "House Rent Allowance", "field_type": "number", "required": False},
                            {"field_id": "conveyance_allowance", "field_name": "Conveyance Allowance", "field_type": "number", "required": False},
                            {"field_id": "medical_allowance", "field_name": "Medical Allowance", "field_type": "number", "required": False},
                            {"field_id": "other_allowances", "field_name": "Other Allowances", "field_type": "number", "required": False}
                        ]
                    }
                ],
                "validation_rules": {
                    "tin": {"pattern": "^[0-9]{12}$", "message": "TIN must be 12 digits"},
                    "salary_income": {"min": 0, "message": "Salary income cannot be negative"}
                },
                "created_at": datetime.utcnow(),
                "status": "active"
            }
        ]
        
        collection = self.database["form_templates"]
        for form in forms:
            existing = await collection.find_one({"form_id": form["form_id"]})
            if not existing:
                await collection.insert_one(form)
                logger.info(f"Seeded form template: {form['form_id']}")
    
    async def validate_setup(self):
        """Validate database setup."""
        try:
            # Check collections
            collections = await self.database.list_collection_names()
            expected_collections = {
                "legal_documents", "document_embeddings", "tax_rules", 
                "tax_slabs", "exemptions_rebates", "user_sessions",
                "calculation_history", "agent_logs", "agent_cache",
                "form_templates", "compliance_tracking", "legal_precedents"
            }
            
            missing_collections = expected_collections - set(collections)
            if missing_collections:
                logger.warning(f"Missing collections: {missing_collections}")
            else:
                logger.info("✅ All collections created successfully")
            
            # Check sample data
            tax_slabs_count = await self.database["tax_slabs"].count_documents({})
            tax_rules_count = await self.database["tax_rules"].count_documents({})
            exemptions_count = await self.database["exemptions_rebates"].count_documents({})
            
            logger.info(f"Database validation:")
            logger.info(f"  - Collections: {len(collections)}")
            logger.info(f"  - Tax slabs: {tax_slabs_count}")
            logger.info(f"  - Tax rules: {tax_rules_count}")
            logger.info(f"  - Exemptions: {exemptions_count}")
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")

async def main():
    """Main initialization function."""
    print("🚀 Initializing AI Tax Lawyer Bangladesh Database...")
    
    initializer = DatabaseInitializer()
    success = await initializer.initialize_database()
    
    if success:
        print("✅ Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Configure RAGFlow instance")
        print("2. Migrate legal documents")
        print("3. Generate embeddings")
        print("4. Test agent framework")
    else:
        print("❌ Database initialization failed!")
        print("Check logs for error details.")

if __name__ == "__main__":
    asyncio.run(main())