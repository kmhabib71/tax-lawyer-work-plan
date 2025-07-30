#!/usr/bin/env python3
"""
Bangladesh Tax Calculation API Server Startup Script
===================================================

This script provides an enhanced way to start the tax calculation API server
with proper configuration, health checks, and monitoring.

Usage:
    python start_api_server.py [--port PORT] [--host HOST] [--workers WORKERS]
"""

import argparse
import os
import sys
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are available"""
    required_files = [
        "comprehensive_tax_engine_2024_25.py",
        "tax_api_backend.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing Python dependencies: {e}")
        print("   Please run: pip install -r requirements.txt")
        return False

def check_circular_data():
    """Check if circular data file is available"""
    circular_file = "income_tax_circular_2024_25_complete.json"
    if Path(circular_file).exists():
        print(f"✅ Circular data file found: {circular_file}")
        return True
    else:
        print(f"⚠️ Circular data file not found: {circular_file}")
        print("   API will use default configuration")
        return False

def start_server(host="0.0.0.0", port=8000, workers=1, reload=True):
    """Start the FastAPI server"""
    import uvicorn
    
    print(f"🚀 Starting Bangladesh Tax Calculation API Server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Workers: {workers}")
    print(f"   Reload: {reload}")
    print(f"   API Documentation: http://localhost:{port}/docs")
    print(f"   Alternative Docs: http://localhost:{port}/redoc")
    
    try:
        uvicorn.run(
            "tax_api_backend:app",
            host=host,
            port=port,
            workers=workers if not reload else 1,  # Multi-worker mode conflicts with reload
            reload=reload,
            access_log=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n⚠️ Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

def test_server(port=8000, max_retries=30):
    """Test if server is responding"""
    base_url = f"http://localhost:{port}"
    
    print(f"🔍 Testing server connectivity...")
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Server is healthy: {result.get('status', 'unknown')}")
                return True
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                print(f"   Retry {i + 1}/{max_retries}...")
                time.sleep(1)
            continue
    
    print(f"❌ Server health check failed after {max_retries} retries")
    return False

def run_quick_test(port=8000):
    """Run a quick tax calculation test"""
    print(f"🧪 Running quick tax calculation test...")
    
    test_data = {
        "taxpayer": {
            "name": "Test User",
            "tin": "123456789012",
            "nid": "1234567890123",
            "category": "individual",
            "age": 30,
            "gender": "male",
            "marital_status": "single",
            "location": "dhaka_city"
        },
        "income": {
            "basic_salary": 500000
        }
    }
    
    try:
        response = requests.post(
            f"http://localhost:{port}/calculate-tax",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Tax calculation test passed")
                print(f"   Total Income: ₹{result['total_income']:,.2f}")
                print(f"   Tax Payable: ₹{result['tax_payable']:,.2f}")
                return True
            else:
                print(f"❌ Tax calculation failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Test request failed: {e}")
    
    return False

def create_systemd_service(port=8000, user="www-data"):
    """Generate systemd service file for production deployment"""
    current_dir = Path.cwd()
    
    service_content = f"""[Unit]
Description=Bangladesh Tax Calculation API
After=network.target

[Service]
Type=exec
User={user}
Group={user}
WorkingDirectory={current_dir}
Environment=PATH={current_dir}/venv/bin
ExecStart={current_dir}/venv/bin/python -m uvicorn tax_api_backend:app --host 0.0.0.0 --port {port} --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "bangladesh-tax-api.service"
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print(f"📝 Systemd service file created: {service_file}")
    print(f"   To install:")
    print(f"   sudo cp {service_file} /etc/systemd/system/")
    print(f"   sudo systemctl daemon-reload")
    print(f"   sudo systemctl enable bangladesh-tax-api")
    print(f"   sudo systemctl start bangladesh-tax-api")

def main():
    parser = argparse.ArgumentParser(
        description="Bangladesh Tax Calculation API Server Startup"
    )
    parser.add_argument(
        "--port", "-p", 
        type=int, 
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload in development mode"
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Only run connectivity and calculation tests"
    )
    parser.add_argument(
        "--create-service",
        action="store_true",
        help="Create systemd service file for production"
    )
    
    args = parser.parse_args()
    
    print("Bangladesh Tax Calculation API Server")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check circular data
    check_circular_data()
    
    # Create systemd service if requested
    if args.create_service:
        create_systemd_service(args.port)
        return
    
    # Test mode
    if args.test_only:
        if test_server(args.port):
            if run_quick_test(args.port):
                print(f"🎉 All tests passed! API is ready for use.")
            else:
                print(f"⚠️ Server is running but calculation test failed")
        return
    
    # Start server
    reload = not args.no_reload
    start_server(
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=reload
    )

if __name__ == "__main__":
    main()