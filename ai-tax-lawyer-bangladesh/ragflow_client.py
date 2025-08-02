#!/usr/bin/env python3
"""
RAGFlow Client for Bangladesh Tax Law System
Optimized for existing RAGFlow instance integration
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGFlowClient:
    """
    Client for interacting with RAGFlow API
    Handles knowledge base operations and document processing
    """
    
    def __init__(self, 
                 base_url: str = "http://localhost:9380",
                 api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
    
    def health_check(self) -> bool:
        """Check if RAGFlow server is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def create_knowledge_base(self, name: str, description: str = "") -> Dict:
        """Create a new knowledge base"""
        payload = {
            "name": name,
            "description": description,
            "chunk_method": "naive",
            "parser_id": "general",
            "language": "English"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/knowledge_bases",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create knowledge base: {e}")
            raise
    
    def list_knowledge_bases(self) -> List[Dict]:
        """List all knowledge bases"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/knowledge_bases")
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Failed to list knowledge bases: {e}")
            return []
    
    def upload_document(self, kb_id: str, file_path: str, file_name: str = None) -> Dict:
        """Upload a document to knowledge base"""
        if not file_name:
            file_name = Path(file_path).name
            
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'application/json')}
                response = self.session.post(
                    f"{self.base_url}/api/v1/knowledge_bases/{kb_id}/documents",
                    files=files
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to upload document {file_path}: {e}")
            raise
    
    def upload_json_content(self, kb_id: str, content: Dict, file_name: str) -> Dict:
        """Upload JSON content directly to knowledge base"""
        try:
            # Convert to text format for RAGFlow
            text_content = self._json_to_text(content)
            
            # Create temporary file
            temp_file = f"/tmp/{file_name}.txt"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            # Upload the file
            result = self.upload_document(kb_id, temp_file, file_name)
            
            # Cleanup
            os.remove(temp_file)
            
            return result
        except Exception as e:
            logger.error(f"Failed to upload JSON content: {e}")
            raise
    
    def _json_to_text(self, content: Dict) -> str:
        """Convert JSON legal content to searchable text"""
        text_parts = []
        
        # Add title and metadata
        if 'title' in content:
            text_parts.append(f"Title: {content['title']}")
        
        if 'act_name' in content:
            text_parts.append(f"Act: {content['act_name']}")
            
        if 'section' in content:
            text_parts.append(f"Section: {content['section']}")
        
        # Add main content
        if 'content' in content:
            if isinstance(content['content'], str):
                text_parts.append(f"Content: {content['content']}")
            elif isinstance(content['content'], dict):
                for key, value in content['content'].items():
                    if isinstance(value, str):
                        text_parts.append(f"{key}: {value}")
        
        # Add schedules if present
        if 'schedules' in content:
            for schedule in content['schedules']:
                if isinstance(schedule, dict):
                    text_parts.append(f"Schedule: {schedule.get('title', 'N/A')}")
                    text_parts.append(f"Details: {schedule.get('content', 'N/A')}")
        
        # Add keywords for better search
        if 'keywords' in content:
            text_parts.append(f"Keywords: {', '.join(content['keywords'])}")
        
        return "\n\n".join(text_parts)
    
    def search(self, kb_id: str, query: str, limit: int = 10) -> List[Dict]:
        """Search documents in knowledge base"""
        payload = {
            "question": query,
            "kb_ids": [kb_id],
            "top_k": limit
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/retrieval",
                json=payload
            )
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def chat(self, kb_id: str, question: str, session_id: str = None) -> Dict:
        """Chat with knowledge base"""
        payload = {
            "question": question,
            "kb_ids": [kb_id],
            "session_id": session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/chat",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise

class TaxLawRAGSetup:
    """
    Setup class for Bangladesh Tax Law RAGFlow integration
    """
    
    def __init__(self, ragflow_client: RAGFlowClient):
        self.client = ragflow_client
        self.kb_id = None
        self.kb_name = "Bangladesh_Tax_Laws_2024"
    
    def setup_knowledge_base(self) -> str:
        """Setup tax law knowledge base"""
        logger.info("Setting up Bangladesh Tax Laws knowledge base...")
        
        # Check if KB already exists
        existing_kbs = self.client.list_knowledge_bases()
        for kb in existing_kbs:
            if kb.get('name') == self.kb_name:
                self.kb_id = kb['id']
                logger.info(f"Found existing knowledge base: {self.kb_id}")
                return self.kb_id
        
        # Create new KB
        kb_result = self.client.create_knowledge_base(
            name=self.kb_name,
            description="Comprehensive Bangladesh Tax Laws including Income Tax Act 2023, Finance Ordinance 2025, Customs Act 2023, and VAT & SD Act 2012"
        )
        
        self.kb_id = kb_result['id']
        logger.info(f"Created new knowledge base: {self.kb_id}")
        return self.kb_id
    
    def upload_legal_documents(self, data_dir: str) -> Dict:
        """Upload all legal documents from data directory"""
        if not self.kb_id:
            self.setup_knowledge_base()
        
        data_path = Path(data_dir)
        results = {
            'uploaded': 0,
            'failed': 0,
            'files': []
        }
        
        logger.info(f"Uploading documents from: {data_path}")
        
        # Find all JSON files
        json_files = list(data_path.glob("*.json"))
        
        for json_file in json_files:
            try:
                logger.info(f"Processing: {json_file.name}")
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                # Upload to RAGFlow
                result = self.client.upload_json_content(
                    self.kb_id, 
                    content, 
                    json_file.stem
                )
                
                results['uploaded'] += 1
                results['files'].append({
                    'file': json_file.name,
                    'status': 'success',
                    'doc_id': result.get('id')
                })
                
                logger.info(f"✅ Uploaded: {json_file.name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to upload {json_file.name}: {e}")
                results['failed'] += 1
                results['files'].append({
                    'file': json_file.name,
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"Upload complete: {results['uploaded']} success, {results['failed']} failed")
        return results

def main():
    """Test RAGFlow integration"""
    print("🚀 Testing RAGFlow Integration for Bangladesh Tax Laws")
    
    # Initialize client
    client = RAGFlowClient()
    
    # Health check
    if not client.health_check():
        print("❌ RAGFlow server not accessible. Please start RAGFlow first.")
        print("💡 To start RAGFlow:")
        print("   cd /mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ragflow")
        print("   docker-compose up -d")
        return
    
    print("✅ RAGFlow server is running")
    
    # Setup knowledge base
    setup = TaxLawRAGSetup(client)
    kb_id = setup.setup_knowledge_base()
    print(f"✅ Knowledge base ready: {kb_id}")
    
    # Upload documents
    data_dir = "../ragflow/phase0_foundation/data_assets"
    results = setup.upload_legal_documents(data_dir)
    
    print(f"\n📊 Upload Results:")
    print(f"   ✅ Uploaded: {results['uploaded']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    # Test search
    print("\n🔍 Testing search functionality...")
    search_results = client.search(kb_id, "income tax rates 2024", limit=3)
    print(f"Found {len(search_results)} results for 'income tax rates 2024'")
    
    # Test chat
    print("\n💬 Testing chat functionality...")
    chat_result = client.chat(kb_id, "What are the current income tax rates in Bangladesh?")
    print(f"Chat response: {chat_result.get('answer', 'No response')[:200]}...")
    
    print("\n🎉 RAGFlow integration test complete!")

if __name__ == "__main__":
    main()