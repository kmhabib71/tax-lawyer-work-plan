"""
Base agent class for AI Tax Lawyer Bangladesh multi-agent system.
Provides common functionality for all agents.
"""
import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
import json
import hashlib

from config.settings import settings, AgentConfig
from ragflow_integration.client import RAGFlowClient
from utils.logging_utils import (
    get_agent_logger, 
    log_agent_performance, 
    ContextualLogger
)

class AgentType(Enum):
    """Agent type enumeration."""
    SENIOR = "senior"
    JUNIOR_LAWYER = "junior_lawyer"
    MICRO_AGENT = "micro_agent"
    HELPER = "helper"

class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    BUSY = "busy"

class AgentMessage:
    """Standard message format for inter-agent communication."""
    
    def __init__(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        content: Any,
        priority: int = 1,
        correlation_id: str = None
    ):
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.content = content
        self.priority = priority
        self.correlation_id = correlation_id or self._generate_correlation_id()
        self.timestamp = datetime.utcnow()
    
    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID."""
        timestamp = str(int(time.time() * 1000))
        content_hash = hashlib.md5(str(self.content).encode()).hexdigest()[:8]
        return f"msg_{timestamp}_{content_hash}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type,
            "content": self.content,
            "priority": self.priority,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat()
        }

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        specialization: List[str] = None,
        ragflow_collections: List[str] = None,
        rule_coverage: float = 0.5,
        llm_threshold: float = 0.7
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.specialization = specialization or []
        self.ragflow_collections = ragflow_collections or []
        self.rule_coverage = rule_coverage
        self.llm_threshold = llm_threshold
        
        # Agent state
        self.status = AgentStatus.IDLE
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.request_count = 0
        self.error_count = 0
        
        # Performance metrics
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_response_time": 0.0,
            "cache_hit_rate": 0.0,
            "accuracy_score": 0.0
        }
        
        # Dependencies
        self.ragflow_client: Optional[RAGFlowClient] = None
        self.message_queue: List[AgentMessage] = []
        self.cache: Dict[str, Any] = {}
        
        # Logging
        self.logger = ContextualLogger(f"agent.{self.agent_id}")
        self.logger.add_context(
            agent_id=self.agent_id,
            agent_type=self.agent_type.value,
            specialization=",".join(self.specialization)
        )
    
    async def initialize(self) -> bool:
        """Initialize the agent with required dependencies."""
        try:
            self.logger.info("Initializing agent...")
            
            # Initialize RAGFlow client if collections are specified
            if self.ragflow_collections:
                self.ragflow_client = RAGFlowClient()
                
                # Test RAGFlow connection
                if not await self.ragflow_client.health_check():
                    self.logger.warning("RAGFlow health check failed")
            
            # Agent-specific initialization
            init_success = await self._initialize_agent()
            
            if init_success:
                self.logger.info("Agent initialized successfully")
                return True
            else:
                self.logger.error("Agent initialization failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during agent initialization: {e}")
            return False
    
    @abstractmethod
    async def _initialize_agent(self) -> bool:
        """Agent-specific initialization logic."""
        pass
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a request and return response."""
        start_time = time.time()
        request_id = self._generate_request_id(request)
        
        self.logger.add_context(request_id=request_id)
        self.logger.info(f"Processing request: {request.get('type', 'unknown')}")
        
        try:
            # Update agent state
            self.status = AgentStatus.PROCESSING
            self.last_activity = datetime.utcnow()
            self.request_count += 1
            
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_response = self.cache.get(cache_key)
            
            if cached_response:
                self.logger.info("Cache hit - returning cached response")
                response = cached_response
                cache_hit = True
            else:
                # Process request
                response = await self._process_request(request, context or {})
                
                # Cache successful responses
                if response.get("success", False):
                    self.cache[cache_key] = response
                    self._cleanup_cache()
                
                cache_hit = False
            
            # Update performance metrics
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            self._update_performance_metrics(response_time, cache_hit, response.get("success", False))
            
            # Log performance
            log_agent_performance(
                agent_name=self.agent_id,
                query=str(request.get("query", ""))[:100],
                response_time_ms=int(response_time),
                tokens_used=response.get("tokens_used", 0),
                cache_hit=cache_hit,
                success=response.get("success", False),
                error_message=response.get("error") if not response.get("success") else None
            )
            
            self.status = AgentStatus.IDLE
            return response
            
        except Exception as e:
            self.error_count += 1
            self.status = AgentStatus.ERROR
            
            error_response = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.error(f"Request processing failed: {e}")
            
            # Log error performance
            response_time = (time.time() - start_time) * 1000
            log_agent_performance(
                agent_name=self.agent_id,
                query=str(request.get("query", ""))[:100],
                response_time_ms=int(response_time),
                success=False,
                error_message=str(e)
            )
            
            return error_response
        finally:
            self.logger.remove_context("request_id")
    
    @abstractmethod
    async def _process_request(
        self,
        request: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Agent-specific request processing logic."""
        pass
    
    async def get_knowledge(
        self,
        query: str,
        collection: str = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge from RAGFlow."""
        if not self.ragflow_client:
            self.logger.warning("RAGFlow client not initialized")
            return []
        
        try:
            # Use agent's default collections if none specified
            target_collection = collection or (
                self.ragflow_collections[0] if self.ragflow_collections else None
            )
            
            results = await self.ragflow_client.search(
                query=query,
                collection=target_collection,
                top_k=top_k
            )
            
            self.logger.info(f"Retrieved {len(results)} knowledge items for query")
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving knowledge: {e}")
            return []
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message to another agent."""
        try:
            # In a full implementation, this would use a message bus
            # For now, we'll log the message
            self.logger.info(f"Sending message to {message.recipient}: {message.message_type}")
            
            # Add to message queue (placeholder for message bus)
            self.message_queue.append(message)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    async def receive_messages(self) -> List[AgentMessage]:
        """Receive pending messages."""
        messages = self.message_queue.copy()
        self.message_queue.clear()
        return messages
    
    def assess_complexity(self, request: Dict[str, Any]) -> float:
        """Assess the complexity of a request (0.0 = simple, 1.0 = complex)."""
        complexity_factors = []
        
        # Query length factor
        query = str(request.get("query", ""))
        query_factor = min(len(query) / 1000, 1.0)
        complexity_factors.append(query_factor)
        
        # Number of parameters factor
        params = request.get("parameters", {})
        param_factor = min(len(params) / 10, 1.0)
        complexity_factors.append(param_factor)
        
        # Request type factor
        request_type = request.get("type", "")
        type_complexity = {
            "simple_calculation": 0.1,
            "complex_calculation": 0.7,
            "legal_analysis": 0.8,
            "multi_domain": 0.9,
            "precedent_search": 0.6
        }
        complexity_factors.append(type_complexity.get(request_type, 0.5))
        
        # Calculate weighted average
        return sum(complexity_factors) / len(complexity_factors)
    
    def should_use_llm(self, complexity_score: float) -> bool:
        """Determine if LLM should be used based on complexity."""
        return complexity_score >= self.llm_threshold
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "specialization": self.specialization,
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds(),
            "last_activity": self.last_activity.isoformat(),
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "performance_metrics": self.performance_metrics,
            "cache_size": len(self.cache),
            "pending_messages": len(self.message_queue)
        }
    
    async def cleanup(self) -> bool:
        """Cleanup agent resources."""
        try:
            self.logger.info("Cleaning up agent resources...")
            
            # Close RAGFlow client
            if self.ragflow_client:
                await self.ragflow_client.close()
            
            # Clear cache
            self.cache.clear()
            
            # Clear message queue
            self.message_queue.clear()
            
            # Agent-specific cleanup
            await self._cleanup_agent()
            
            self.logger.info("Agent cleanup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during agent cleanup: {e}")
            return False
    
    async def _cleanup_agent(self):
        """Agent-specific cleanup logic."""
        pass
    
    # Helper methods
    
    def _generate_request_id(self, request: Dict[str, Any]) -> str:
        """Generate unique request ID."""
        timestamp = str(int(time.time() * 1000))
        content = str(request.get("query", ""))[:50]
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{self.agent_id}_{timestamp}_{content_hash}"
    
    def _generate_cache_key(self, request: Dict[str, Any]) -> str:
        """Generate cache key for request."""
        # Create deterministic key from request content
        key_data = {
            "query": request.get("query", ""),
            "type": request.get("type", ""),
            "parameters": request.get("parameters", {})
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _cleanup_cache(self):
        """Clean up cache to prevent memory issues."""
        max_cache_size = 100
        
        if len(self.cache) > max_cache_size:
            # Remove oldest entries (simple FIFO for now)
            items_to_remove = len(self.cache) - max_cache_size
            cache_keys = list(self.cache.keys())
            
            for key in cache_keys[:items_to_remove]:
                del self.cache[key]
    
    def _update_performance_metrics(
        self,
        response_time: float,
        cache_hit: bool,
        success: bool
    ):
        """Update agent performance metrics."""
        metrics = self.performance_metrics
        
        # Update counters
        metrics["total_requests"] += 1
        if success:
            metrics["successful_requests"] += 1
        
        # Update average response time
        current_avg = metrics["average_response_time"]
        total_requests = metrics["total_requests"]
        metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
        # Update cache hit rate
        cache_hits = getattr(self, '_cache_hits', 0)
        if cache_hit:
            cache_hits += 1
            self._cache_hits = cache_hits
        
        metrics["cache_hit_rate"] = cache_hits / total_requests
        
        # Update accuracy score (simplified)
        if success:
            current_accuracy = metrics["accuracy_score"]
            metrics["accuracy_score"] = (
                (current_accuracy * (metrics["successful_requests"] - 1) + 1.0) /
                metrics["successful_requests"]
            )

class AgentRegistry:
    """Registry for managing active agents."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("agent.registry")
    
    def register_agent(self, agent: BaseAgent) -> bool:
        """Register an agent with the registry."""
        try:
            if agent.agent_id in self.agents:
                self.logger.warning(f"Agent {agent.agent_id} already registered")
                return False
            
            self.agents[agent.agent_id] = agent
            self.logger.info(f"Registered agent: {agent.agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering agent {agent.agent_id}: {e}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the registry."""
        try:
            if agent_id not in self.agents:
                self.logger.warning(f"Agent {agent_id} not found in registry")
                return False
            
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent: {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unregistering agent {agent_id}: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """Get all agents of a specific type."""
        return [
            agent for agent in self.agents.values()
            if agent.agent_type == agent_type
        ]
    
    def get_agents_by_specialization(self, specialization: str) -> List[BaseAgent]:
        """Get all agents with a specific specialization."""
        return [
            agent for agent in self.agents.values()
            if specialization in agent.specialization
        ]
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents."""
        return list(self.agents.values())
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics for all agents."""
        stats = {
            "total_agents": len(self.agents),
            "agents_by_type": {},
            "agents_by_status": {},
            "total_requests": 0,
            "total_errors": 0
        }
        
        for agent in self.agents.values():
            # Count by type
            agent_type = agent.agent_type.value
            stats["agents_by_type"][agent_type] = stats["agents_by_type"].get(agent_type, 0) + 1
            
            # Count by status
            status = agent.status.value
            stats["agents_by_status"][status] = stats["agents_by_status"].get(status, 0) + 1
            
            # Aggregate metrics
            stats["total_requests"] += agent.request_count
            stats["total_errors"] += agent.error_count
        
        return stats

# Global agent registry instance
agent_registry = AgentRegistry()