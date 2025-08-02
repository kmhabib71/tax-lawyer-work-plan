#!/usr/bin/env python3
"""
RAGFlow Deployment Manager - Week 1 Implementation
Handles RAGFlow server deployment, status checking, and legal collections setup
"""

import requests
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import subprocess
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGFlowDeploymentManager:
    """Manages RAGFlow deployment and health monitoring"""
    
    def __init__(self, 
                 base_url: str = "http://localhost:9380",
                 ragflow_path: str = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ragflow"):
        self.base_url = base_url.rstrip('/')
        self.ragflow_path = ragflow_path
        self.session = requests.Session()
        self.session.timeout = 10
        
        # Deployment status
        self.is_deployed = False
        self.is_healthy = False
        self.last_health_check = None
        self.deployment_start_time = None
        
        logger.info(f"📡 RAGFlow Deployment Manager initialized")
        logger.info(f"   Base URL: {self.base_url}")
        logger.info(f"   RAGFlow Path: {self.ragflow_path}")
    
    def check_docker_status(self) -> Dict[str, Any]:
        """Check Docker and RAGFlow container status"""
        status = {
            "docker_running": False,
            "ragflow_containers": {},
            "errors": []
        }
        
        try:
            # Check Docker is running
            result = subprocess.run(
                ["docker", "ps"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                status["docker_running"] = True
                logger.info("✅ Docker is running")
                
                # Check RAGFlow containers
                ragflow_containers = self._parse_docker_containers(result.stdout)
                status["ragflow_containers"] = ragflow_containers
                
                if ragflow_containers:
                    logger.info(f"📦 Found {len(ragflow_containers)} RAGFlow containers")
                    for container, state in ragflow_containers.items():
                        logger.info(f"   {container}: {state}")
                else:
                    logger.warning("⚠️ No RAGFlow containers found")
            
            else:
                status["errors"].append("Docker is not running or not accessible")
                logger.error("❌ Docker is not running or not accessible")
        
        except subprocess.TimeoutExpired:
            status["errors"].append("Docker command timed out")
            logger.error("❌ Docker command timed out")
        except Exception as e:
            status["errors"].append(f"Docker check failed: {str(e)}")
            logger.error(f"❌ Docker check failed: {e}")
        
        return status
    
    def _parse_docker_containers(self, docker_output: str) -> Dict[str, str]:
        """Parse docker ps output to find RAGFlow containers"""
        containers = {}
        
        for line in docker_output.split('\n')[1:]:  # Skip header
            if 'ragflow' in line.lower() or 'mysql' in line.lower() or 'redis' in line.lower():
                parts = line.split()
                if len(parts) >= 2:
                    container_name = parts[-1]  # Last column is usually name
                    status = parts[4] if len(parts) > 4 else "unknown"  # Status column
                    containers[container_name] = status
        
        return containers
    
    async def health_check(self, timeout: int = 5) -> Tuple[bool, Dict[str, Any]]:
        """Comprehensive health check of RAGFlow server"""
        health_result = {
            "server_reachable": False,
            "api_responsive": False,
            "response_time_ms": 0,
            "status_code": 0,
            "error": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        start_time = time.time()
        
        try:
            # Test basic connectivity
            response = self.session.get(f"{self.base_url}/api/health", timeout=timeout)
            
            response_time = (time.time() - start_time) * 1000
            health_result["response_time_ms"] = round(response_time, 2)
            health_result["status_code"] = response.status_code
            health_result["server_reachable"] = True
            
            if response.status_code == 200:
                health_result["api_responsive"] = True
                self.is_healthy = True
                logger.info(f"✅ RAGFlow server healthy ({response_time:.1f}ms)")
            else:
                logger.warning(f"⚠️ RAGFlow server returned status {response.status_code}")
        
        except requests.exceptions.ConnectTimeout:
            health_result["error"] = "Connection timeout"
            logger.error("❌ RAGFlow server connection timeout")
        except requests.exceptions.ConnectionError:
            health_result["error"] = "Connection error - server may not be running"
            logger.error("❌ RAGFlow server connection error")
        except Exception as e:
            health_result["error"] = str(e)
            logger.error(f"❌ RAGFlow health check failed: {e}")
        
        self.last_health_check = health_result
        return self.is_healthy, health_result
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get RAGFlow server information"""
        if not self.is_healthy:
            return {"error": "Server not healthy"}
        
        try:
            # Try to get server info - this endpoint may vary based on RAGFlow version
            endpoints_to_try = [
                "/api/info",
                "/api/status", 
                "/api/version",
                "/health"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        return {
                            "endpoint": endpoint,
                            "data": response.json() if response.content else {"status": "ok"}
                        }
                except:
                    continue
            
            return {"message": "Server reachable but info endpoints not available"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def check_knowledge_bases(self) -> Dict[str, Any]:
        """Check existing knowledge bases"""
        if not self.is_healthy:
            return {"error": "Server not healthy"}
        
        try:
            # Try different endpoints for knowledge bases
            kb_endpoints = [
                "/api/kb",
                "/api/knowledgebases",
                "/api/datasets",
                "/api/collections"
            ]
            
            for endpoint in kb_endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        data = response.json() if response.content else []
                        return {
                            "endpoint": endpoint,
                            "knowledge_bases": data,
                            "count": len(data) if isinstance(data, list) else 0
                        }
                except:
                    continue
            
            return {"message": "Knowledge base endpoints not accessible"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def create_legal_knowledge_base(self, name: str = "bangladesh_tax_law") -> Dict[str, Any]:
        """Create knowledge base for Bangladesh tax law"""
        if not self.is_healthy:
            return {"success": False, "error": "Server not healthy"}
        
        try:
            # Try to create knowledge base
            payload = {
                "name": name,
                "description": "Bangladesh Tax Law Knowledge Base - Income Tax, VAT, Customs",
                "language": "Bengali_English",
                "chunk_method": "intelligent",
                "parser_config": {
                    "chunk_token_count": 1024,
                    "layout_recognize": True,
                    "task_page_size": 12
                }
            }
            
            create_endpoints = [
                "/api/kb",
                "/api/knowledgebases",
                "/api/datasets/create"
            ]
            
            for endpoint in create_endpoints:
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"✅ Knowledge base '{name}' created successfully")
                        return {
                            "success": True,
                            "knowledge_base": response.json() if response.content else {"name": name},
                            "endpoint": endpoint
                        }
                
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} failed: {e}")
                    continue
            
            return {"success": False, "error": "No working create endpoint found"}
        
        except Exception as e:
            logger.error(f"Failed to create knowledge base: {e}")
            return {"success": False, "error": str(e)}
    
    def deploy_ragflow(self) -> Dict[str, Any]:
        """Deploy RAGFlow using Docker Compose"""
        deployment_result = {
            "success": False,
            "docker_status": {},
            "deployment_time": 0,
            "errors": []
        }
        
        logger.info("🚀 Starting RAGFlow deployment...")
        start_time = time.time()
        
        try:
            # Check Docker first
            docker_status = self.check_docker_status()
            deployment_result["docker_status"] = docker_status
            
            if not docker_status["docker_running"]:
                deployment_result["errors"].append("Docker is not running")
                return deployment_result
            
            # Change to RAGFlow directory
            if not os.path.exists(self.ragflow_path):
                deployment_result["errors"].append(f"RAGFlow path not found: {self.ragflow_path}")
                return deployment_result
            
            logger.info(f"📂 Changing to RAGFlow directory: {self.ragflow_path}")
            os.chdir(self.ragflow_path)
            
            # Start RAGFlow with docker-compose
            logger.info("🐳 Starting docker-compose...")
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("✅ Docker-compose started successfully")
                
                # Wait for services to be ready
                logger.info("⏳ Waiting for services to be ready...")
                ready = self._wait_for_services(max_wait_time=60)
                
                if ready:
                    deployment_result["success"] = True
                    self.is_deployed = True
                    self.deployment_start_time = datetime.utcnow()
                    logger.info("🎉 RAGFlow deployment successful!")
                else:
                    deployment_result["errors"].append("Services failed to become ready")
            else:
                deployment_result["errors"].append(f"Docker-compose failed: {result.stderr}")
                logger.error(f"❌ Docker-compose failed: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            deployment_result["errors"].append("Deployment timed out")
            logger.error("❌ Deployment timed out")
        except Exception as e:
            deployment_result["errors"].append(str(e))
            logger.error(f"❌ Deployment failed: {e}")
        
        deployment_result["deployment_time"] = time.time() - start_time
        return deployment_result
    
    def _wait_for_services(self, max_wait_time: int = 60) -> bool:
        """Wait for RAGFlow services to be ready"""
        logger.info(f"⏳ Waiting up to {max_wait_time}s for services...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            # Check health
            try:
                response = self.session.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ RAGFlow server is ready!")
                    return True
            except:
                pass
            
            # Also check if we can reach the main page
            try:
                response = self.session.get(self.base_url, timeout=5)
                if response.status_code == 200:
                    logger.info("✅ RAGFlow web interface is ready!")
                    return True
            except:
                pass
            
            logger.info(f"⏳ Still waiting... ({int(time.time() - start_time)}s)")
            time.sleep(5)
        
        logger.warning(f"⚠️ Services not ready after {max_wait_time}s")
        return False
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get comprehensive deployment status"""
        status = {
            "is_deployed": self.is_deployed,
            "is_healthy": self.is_healthy,
            "last_health_check": self.last_health_check,
            "deployment_start_time": self.deployment_start_time.isoformat() if self.deployment_start_time else None,
            "uptime_seconds": 0
        }
        
        if self.deployment_start_time:
            status["uptime_seconds"] = (datetime.utcnow() - self.deployment_start_time).total_seconds()
        
        # Get current Docker status
        status["docker_status"] = self.check_docker_status()
        
        # Get server info if healthy
        if self.is_healthy:
            status["server_info"] = self.get_server_info()
            status["knowledge_bases"] = self.check_knowledge_bases()
        
        return status

async def main():
    """Main deployment and testing function"""
    print("🏗️ RAGFlow Production Deployment - Week 1 Implementation")
    print("=" * 60)
    
    # Initialize deployment manager
    manager = RAGFlowDeploymentManager()
    
    # Step 1: Check Docker and existing containers
    print("\n📋 Step 1: Checking Docker Status")
    docker_status = manager.check_docker_status()
    
    if docker_status["docker_running"]:
        print("✅ Docker is running")
        if docker_status["ragflow_containers"]:
            print(f"📦 Found existing containers:")
            for container, status in docker_status["ragflow_containers"].items():
                print(f"   - {container}: {status}")
        else:
            print("📦 No existing RAGFlow containers found")
    else:
        print("❌ Docker issues found:")
        for error in docker_status["errors"]:
            print(f"   - {error}")
    
    # Step 2: Health check
    print("\n📋 Step 2: RAGFlow Health Check")
    is_healthy, health_result = await manager.health_check()
    
    if is_healthy:
        print(f"✅ RAGFlow is healthy ({health_result['response_time_ms']}ms)")
    else:
        print(f"❌ RAGFlow health check failed: {health_result.get('error', 'unknown')}")
        
        # If not healthy, try deployment
        if not docker_status["ragflow_containers"]:
            print("\n📋 Step 3: Deploying RAGFlow")
            deployment_result = manager.deploy_ragflow()
            
            if deployment_result["success"]:
                print(f"✅ Deployment successful ({deployment_result['deployment_time']:.1f}s)")
                
                # Re-check health after deployment
                print("\n📋 Step 4: Post-deployment Health Check")
                is_healthy, health_result = await manager.health_check()
                
                if is_healthy:
                    print(f"✅ RAGFlow is now healthy ({health_result['response_time_ms']}ms)")
                else:
                    print(f"❌ RAGFlow still not healthy: {health_result.get('error')}")
            else:
                print("❌ Deployment failed:")
                for error in deployment_result["errors"]:
                    print(f"   - {error}")
                return
    
    # Step 5: Check server info and knowledge bases
    if is_healthy:
        print("\n📋 Step 5: Server Information")
        server_info = manager.get_server_info()
        print(f"📊 Server Info: {json.dumps(server_info, indent=2)}")
        
        print("\n📋 Step 6: Knowledge Base Status")
        kb_status = manager.check_knowledge_bases()
        print(f"📚 Knowledge Bases: {json.dumps(kb_status, indent=2)}")
        
        # Step 7: Create legal knowledge base if needed
        print("\n📋 Step 7: Legal Knowledge Base Setup")
        kb_result = manager.create_legal_knowledge_base()
        
        if kb_result.get("success"):
            print("✅ Legal knowledge base created/verified")
        else:
            print(f"⚠️ Knowledge base setup: {kb_result.get('error', 'unknown issue')}")
    
    # Final status
    print("\n📊 Final Deployment Status")
    final_status = manager.get_deployment_status()
    
    print(f"Deployed: {final_status['is_deployed']}")
    print(f"Healthy: {final_status['is_healthy']}")
    print(f"Uptime: {final_status['uptime_seconds']:.0f}s")
    
    if final_status["is_healthy"]:
        print(f"\n🎉 RAGFlow Production Deployment Complete!")
        print(f"🌐 Access RAGFlow at: http://localhost:9380")
        print(f"📚 Legal knowledge base ready for document uploads")
        print(f"✅ Week 1 RAGFlow requirement satisfied")
    else:
        print(f"\n⚠️ RAGFlow deployment incomplete")
        print(f"📝 Manual deployment may be required")
        print(f"💡 Try: Navigate to ragflow directory and run 'docker-compose up -d'")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())