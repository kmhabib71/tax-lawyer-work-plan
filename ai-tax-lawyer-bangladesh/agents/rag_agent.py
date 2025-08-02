#!/usr/bin/env python3
"""
RAG Agent for Bangladesh Tax Law System
Integrates with RAGFlow for knowledge retrieval
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.base.base_agent import BaseAgent, AgentType, agent_registry
from ragflow_client import RAGFlowClient, TaxLawRAGSetup

logger = logging.getLogger(__name__)

@agent_registry.register(AgentType.KNOWLEDGE)
class RAGAgent(BaseAgent):
    """
    RAG Agent for retrieving tax law information using RAGFlow
    """
    
    def __init__(self, name: str = "RAG_Agent"):
        super().__init__(name, AgentType.KNOWLEDGE)
        self.ragflow_client = None
        self.kb_id = None
        self.setup_client()
    
    def setup_client(self):
        """Initialize RAGFlow client"""
        try:
            self.ragflow_client = RAGFlowClient()
            
            # Check if server is running
            if self.ragflow_client.health_check():
                logger.info("✅ RAGFlow client connected successfully")
                self.initialize_knowledge_base()
            else:
                logger.warning("⚠️ RAGFlow server not accessible")
                
        except Exception as e:
            logger.error(f"Failed to setup RAGFlow client: {e}")
            self.ragflow_client = None
    
    def initialize_knowledge_base(self):
        """Initialize or connect to existing knowledge base"""
        try:
            setup = TaxLawRAGSetup(self.ragflow_client)
            self.kb_id = setup.setup_knowledge_base()
            logger.info(f"Knowledge base initialized: {self.kb_id}")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message and retrieve relevant tax law information
        """
        try:
            query = message.get('query', '')
            message_type = message.get('type', 'search')
            
            if not self.ragflow_client or not self.kb_id:
                return {
                    'success': False,
                    'error': 'RAGFlow not available',
                    'message': 'RAGFlow service is not running or knowledge base not initialized'
                }
            
            if message_type == 'search':
                return await self.search_knowledge(query, message.get('limit', 5))
            elif message_type == 'chat':
                return await self.chat_with_knowledge(query, message.get('session_id'))
            else:
                return {
                    'success': False,
                    'error': 'Invalid message type',
                    'supported_types': ['search', 'chat']
                }
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def search_knowledge(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search for relevant tax law information"""
        try:
            logger.info(f"Searching for: {query}")
            
            # Perform search
            search_results = self.ragflow_client.search(self.kb_id, query, limit)
            
            # Format results
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    'content': result.get('content', ''),
                    'source': result.get('source', ''),
                    'score': result.get('score', 0),
                    'metadata': result.get('metadata', {})
                })
            
            return {
                'success': True,
                'query': query,
                'results': formatted_results,
                'count': len(formatted_results)
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    async def chat_with_knowledge(self, question: str, session_id: str = None) -> Dict[str, Any]:
        """Chat with the knowledge base for conversational answers"""
        try:
            logger.info(f"Chat question: {question}")
            
            # Perform chat
            chat_result = self.ragflow_client.chat(self.kb_id, question, session_id)
            
            return {
                'success': True,
                'question': question,
                'answer': chat_result.get('answer', ''),
                'sources': chat_result.get('sources', []),
                'session_id': chat_result.get('session_id', session_id)
            }
            
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'question': question
            }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': self.name,
            'type': self.agent_type.value,
            'description': 'RAG Agent for Bangladesh Tax Law retrieval using RAGFlow',
            'capabilities': [
                'search_tax_laws',
                'conversational_qa',
                'document_retrieval',
                'semantic_search'
            ],
            'supported_message_types': ['search', 'chat'],
            'status': {
                'ragflow_connected': self.ragflow_client is not None and self.ragflow_client.health_check(),
                'knowledge_base_ready': self.kb_id is not None
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health and dependencies"""
        ragflow_status = False
        kb_status = False
        
        if self.ragflow_client:
            ragflow_status = self.ragflow_client.health_check()
            kb_status = self.kb_id is not None
        
        return {
            'agent_name': self.name,
            'status': 'healthy' if ragflow_status and kb_status else 'degraded',
            'ragflow_server': ragflow_status,
            'knowledge_base': kb_status,
            'kb_id': self.kb_id
        }

class TaxLawQueryProcessor:
    """
    High-level processor for tax law queries
    """
    
    def __init__(self):
        self.rag_agent = RAGAgent()
    
    async def process_tax_query(self, query: str, query_type: str = 'search') -> Dict[str, Any]:
        """
        Process a tax law query with intelligent routing
        """
        # Enhance query for better results
        enhanced_query = self.enhance_query(query)
        
        # Create message
        message = {
            'query': enhanced_query,
            'type': query_type,
            'limit': 5
        }
        
        # Process with RAG agent
        result = await self.rag_agent.process_message(message)
        
        # Post-process results
        if result.get('success'):
            result['enhanced_query'] = enhanced_query
            result['original_query'] = query
        
        return result
    
    def enhance_query(self, query: str) -> str:
        """
        Enhance user query for better search results
        """
        # Add context keywords for Bangladesh tax law
        query_lower = query.lower()
        
        # Add relevant context if missing
        enhancements = []
        
        if 'tax' not in query_lower and 'আয়কর' not in query_lower:
            if any(term in query_lower for term in ['rate', 'calculation', 'income']):
                enhancements.append('income tax')
        
        if 'bangladesh' not in query_lower and 'বাংলাদেশ' not in query_lower:
            enhancements.append('Bangladesh')
        
        if '2023' not in query and '২০২৩' not in query and 'act' in query_lower:
            enhancements.append('2023')
        
        # Combine original query with enhancements
        if enhancements:
            enhanced = f"{query} {' '.join(enhancements)}"
        else:
            enhanced = query
        
        return enhanced

async def main():
    """Test RAG Agent"""
    print("🤖 Testing RAG Agent for Bangladesh Tax Laws")
    
    # Initialize processor
    processor = TaxLawQueryProcessor()
    
    # Check agent health
    health = await processor.rag_agent.health_check()
    print(f"📊 Agent Health: {health}")
    
    if health['status'] != 'healthy':
        print("❌ RAG Agent not ready. Please ensure RAGFlow is running.")
        return
    
    # Test queries
    test_queries = [
        "What are the current income tax rates?",
        "Tax deduction for business expenses",
        "VAT registration requirements",
        "Income tax exemption limits"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        
        # Test search
        search_result = await processor.process_tax_query(query, 'search')
        if search_result.get('success'):
            print(f"   ✅ Found {search_result['count']} results")
            if search_result['results']:
                first_result = search_result['results'][0]
                print(f"   📄 Top result: {first_result['content'][:100]}...")
        else:
            print(f"   ❌ Search failed: {search_result.get('error')}")
        
        # Test chat
        chat_result = await processor.process_tax_query(query, 'chat')
        if chat_result.get('success'):
            print(f"   💬 Chat answer: {chat_result['answer'][:100]}...")
        else:
            print(f"   ❌ Chat failed: {chat_result.get('error')}")
    
    print("\n🎉 RAG Agent testing complete!")

if __name__ == "__main__":
    asyncio.run(main())