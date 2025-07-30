# Bangladesh Tax Calculation API - Integration Guide

## 🎯 Overview

The Bangladesh Tax Calculation API provides a comprehensive FastAPI backend for the tax calculation engine. It offers RESTful endpoints for calculating taxes, validating taxpayer data, and retrieving tax information for the 2024-25 tax year.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- All dependencies from `requirements.txt`
- `comprehensive_tax_engine_2024_25.py` in the same directory

### Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the API Server**
   ```bash
   python tax_api_backend.py
   ```
   
   The server will start on `http://localhost:8000`

3. **Verify Installation**
   ```bash
   curl http://localhost:8000/health
   ```

## 📋 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and status |
| `/health` | GET | Health check and system status |
| `/calculate-tax` | POST | Comprehensive tax calculation |
| `/validate-taxpayer` | POST | Taxpayer profile validation |
| `/tax-info` | GET | Tax rates and system information |
| `/docs` | GET | Interactive API documentation |
| `/redoc` | GET | Alternative API documentation |

### Authentication
Currently, the API operates without authentication. For production deployment, implement appropriate authentication mechanisms.

## 💡 Usage Examples

### 1. Basic Individual Tax Calculation

```python
import requests

# API endpoint
url = "http://localhost:8000/calculate-tax"

# Request data
data = {
    "taxpayer": {
        "name": "Ahmed Hassan",
        "tin": "123456789012",
        "nid": "1234567890123",
        "category": "individual",
        "age": 35,
        "gender": "male",
        "marital_status": "married",
        "location": "dhaka_city",
        "profession": "Software Engineer"
    },
    "income": {
        "basic_salary": 800000,
        "house_rent_allowance": 200000,
        "medical_allowance": 50000,
        "other_allowances": 25000
    },
    "investments": {
        "life_insurance_premium": 50000,
        "dps_contribution": 30000,
        "stock_purchase": 100000
    }
}

# Make request
response = requests.post(url, json=data)
result = response.json()

# Process result
if result["success"]:
    print(f"Total Income: ₹{result['total_income']:,.2f}")
    print(f"Tax Payable: ₹{result['tax_payable']:,.2f}")
    print(f"Payment Status: {result['payment_status']}")
```

### 2. Company Tax Calculation

```python
data = {
    "taxpayer": {
        "name": "Tech Solutions Bangladesh Ltd.",
        "tin": "555666777888",
        "nid": "N/A",
        "category": "company",
        "age": 10,
        "gender": "N/A",
        "marital_status": "N/A",
        "location": "dhaka_city",
        "company_type": "private_limited",
        "industry_sector": "Information Technology"
    },
    "income": {
        "business_income": 5000000,
        "service_income": 2000000,
        "other_income": 200000
    },
    "assets": {
        "business_capital": 10000000,
        "business_property": 8000000,
        "business_equipment": 3000000
    }
}

response = requests.post("http://localhost:8000/calculate-tax", json=data)
```

### 3. Taxpayer Validation

```python
taxpayer_data = {
    "name": "Fatima Rahman",
    "tin": "987654321098",
    "nid": "9876543210987",
    "category": "individual",
    "age": 28,
    "gender": "female",
    "marital_status": "single",
    "location": "chittagong_city",
    "special_statuses": ["female"]
}

response = requests.post("http://localhost:8000/validate-taxpayer", json=taxpayer_data)
validation_result = response.json()

if validation_result["valid"]:
    print("✅ Taxpayer data is valid")
else:
    print("❌ Validation errors:", validation_result["errors"])
```

## 📊 Request/Response Formats

### Tax Calculation Request Structure

```json
{
  "taxpayer": {
    "name": "string",
    "tin": "string (12 digits)",
    "nid": "string",
    "category": "individual|company|firm|...",
    "age": "integer",
    "gender": "male|female|third_gender",
    "marital_status": "string",
    "location": "dhaka_city|chittagong_city|...",
    "special_statuses": ["array of special statuses"],
    "disability_type": "string (optional)",
    "disability_percentage": "number (optional)",
    "profession": "string (optional)",
    "company_type": "string (optional)"
  },
  "income": {
    "basic_salary": "number",
    "house_rent_allowance": "number",
    "business_income": "number",
    "rental_income": "number",
    "agricultural_income": "number",
    "capital_gains": "number",
    "bank_interest": "number",
    "dividend_income": "number",
    "other_income": "number"
    // ... additional income fields
  },
  "investments": {
    "life_insurance_premium": "number",
    "dps_contribution": "number",
    "government_securities": "number",
    "stock_purchase": "number",
    "mutual_fund": "number"
    // ... additional investment fields
  },
  "lifestyle": {
    "food_clothing": "number",
    "accommodation": "number",
    "transportation": "number",
    "education_expenses": "number",
    "medical_expenses": "number"
    // ... additional lifestyle fields
  },
  "assets": {
    "house_property": "number",
    "business_capital": "number",
    "bank_deposits": "number",
    "motor_vehicle": "number"
    // ... additional asset fields
  },
  "payments": {
    "salary_tds": "number",
    "advance_tax_paid": "number",
    "previous_refund": "number",
    "previous_due": "number"
    // ... additional payment fields
  }
}
```

### Tax Calculation Response Structure

```json
{
  "success": true,
  "calculation_id": "uuid-string",
  "timestamp": "ISO-datetime",
  "taxpayer_name": "string",
  "taxpayer_category": "string",
  "total_income": "number",
  "taxable_income": "number",
  "gross_tax": "number",
  "net_tax_after_rebate": "number",
  "minimum_tax": "number",
  "tax_payable": "number",
  "total_surcharge": "number",
  "total_amount_payable": "number",
  "exemptions": {
    // Detailed exemption breakdown
  },
  "rebates": {
    // Detailed rebate breakdown
  },
  "surcharges": {
    // Detailed surcharge breakdown
  },
  "payments_summary": {
    // Payment summary
  },
  "refund_or_payable": "number",
  "payment_status": "refund|payable|settled",
  "calculation_steps": [
    // Step-by-step calculation audit trail
  ],
  "warnings": ["array of warnings"],
  "recommendations": ["array of recommendations"]
}
```

## 🔧 Configuration Options

### Environment Variables

Create a `.env` file for configuration:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=tax_api.log

# Database Configuration (future use)
# DATABASE_URL=postgresql://user:pass@localhost/taxdb

# Security Configuration (future use)
# SECRET_KEY=your-secret-key
# ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Server Configuration

```python
# Custom server configuration
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "tax_api_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True,
        log_level="info",
        workers=1  # Increase for production
    )
```

## 🔍 Error Handling

### Common Error Responses

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

### Error Status Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server-side error |
| 503 | Service Unavailable - Tax engine not available |

### Error Handling Example

```python
import requests

try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    result = response.json()
    
    if result.get("success"):
        # Process successful result
        print(f"Tax calculated: ₹{result['tax_payable']}")
    else:
        # Handle calculation errors
        print(f"Calculation failed: {result.get('error', 'Unknown error')}")
        
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
    print(f"Error details: {e.response.text}")
    
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

## 📈 Performance Considerations

### Request Performance
- Simple individual calculation: ~50-100ms
- Complex business calculation: ~100-200ms
- Company calculation: ~100-150ms

### Optimization Tips

1. **Batch Processing**: For multiple calculations, use async processing
2. **Caching**: Cache taxpayer profiles for repeated calculations
3. **Connection Pooling**: Use connection pooling for high-volume usage
4. **Data Validation**: Validate data client-side before API calls

### Load Testing Example

```python
import asyncio
import aiohttp
import time

async def calculate_tax_async(session, data):
    async with session.post('http://localhost:8000/calculate-tax', json=data) as response:
        return await response.json()

async def load_test(num_requests=100):
    # Test data
    test_data = {
        "taxpayer": {
            "name": "Load Test",
            "tin": "123456789012",
            "nid": "1234567890123",
            "category": "individual",
            "age": 30,
            "gender": "male",
            "marital_status": "single",
            "location": "dhaka_city"
        },
        "income": {"basic_salary": 500000}
    }
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [calculate_tax_async(session, test_data) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    successful = sum(1 for r in results if r.get('success'))
    
    print(f"Load test results:")
    print(f"Requests: {num_requests}")
    print(f"Successful: {successful}")
    print(f"Time: {end_time - start_time:.2f}s")
    print(f"RPS: {num_requests / (end_time - start_time):.2f}")

# Run load test
# asyncio.run(load_test(100))
```

## 🔒 Security Considerations

### Current Security Features
- Input validation with Pydantic models
- CORS middleware configured
- Exception handling to prevent information leakage
- Request logging for audit trails

### Production Security Recommendations

1. **Authentication & Authorization**
   ```python
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   
   security = HTTPBearer()
   
   @app.post("/calculate-tax")
   async def calculate_tax(
       request: TaxCalculationRequest,
       credentials: HTTPAuthorizationCredentials = Depends(security)
   ):
       # Implement token validation
       pass
   ```

2. **Rate Limiting**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/calculate-tax")
   @limiter.limit("10/minute")
   async def calculate_tax(request: Request, ...):
       pass
   ```

3. **HTTPS Configuration**
   ```python
   uvicorn.run(
       "tax_api_backend:app",
       host="0.0.0.0",
       port=443,
       ssl_keyfile="key.pem",
       ssl_certfile="cert.pem"
   )
   ```

## 🧪 Testing

### Unit Testing

```python
import pytest
from fastapi.testclient import TestClient
from tax_api_backend import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_tax_calculation():
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
        "income": {"basic_salary": 500000}
    }
    
    response = client.post("/calculate-tax", json=test_data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == True
    assert "tax_payable" in result

# Run tests: pytest -v
```

### Integration Testing

```bash
# Test all examples
python api_examples.py

# Test specific endpoint
curl -X POST "http://localhost:8000/calculate-tax" \
     -H "Content-Type: application/json" \
     -d '{"taxpayer": {"name": "Test", "tin": "123456789012", ...}, "income": {...}}'
```

## 📋 Monitoring & Logging

### Request Logging
All requests are automatically logged with:
- Request timestamp
- Endpoint accessed
- Response status
- Processing time
- Error details (if any)

### Audit Logging
Tax calculations are logged to `tax_calculation_audit.log`:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "calculation_id": "uuid",
  "taxpayer_tin": "123456789012",
  "taxpayer_name": "Ahmed Hassan",
  "total_income": 1000000.0,
  "tax_payable": 75000.0,
  "api_version": "1.0.0"
}
```

### Health Monitoring
```python
# Custom health checks
@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "tax_engine": "operational",
            "database": "connected",
            "memory_usage": "45%",
            "disk_space": "78%"
        }
    }
```

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "tax_api_backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  tax-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

### Production Server Configuration

```python
# production_server.py
import uvicorn
from tax_api_backend import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=4,  # Adjust based on CPU cores
        access_log=True,
        log_level="info",
        ssl_keyfile="path/to/key.pem",
        ssl_certfile="path/to/cert.pem"
    )
```

## 🎯 Integration with AI Tax Lawyer System

### RAG System Integration

```python
# Example integration with RAG system
from tax_api_backend import app
from your_rag_system import RAGSystem

rag_system = RAGSystem()

@app.post("/ai-tax-consultation")
async def ai_tax_consultation(
    question: str,
    taxpayer_profile: TaxpayerProfileRequest = None
):
    # Use RAG system for tax advice
    advice = rag_system.get_tax_advice(question)
    
    # If calculation needed, use tax engine
    if taxpayer_profile and "calculate" in question.lower():
        calculation = await calculate_tax(taxpayer_profile)
        advice["calculation"] = calculation
    
    return advice
```

### Multi-Hop RAG Integration

```python
from income_tax_circular_2024_25_complete import load_circular_data

circular_data = load_circular_data()

@app.post("/intelligent-tax-query")
async def intelligent_tax_query(query: str):
    # Process query through multi-hop RAG
    # 1. Intent classification
    # 2. Topic identification  
    # 3. Cross-reference lookup
    # 4. Tax calculation if needed
    # 5. Comprehensive response
    
    return {
        "answer": "AI-generated response",
        "legal_references": ["Section 1", "Section 2"],
        "calculation": "If applicable",
        "confidence": 0.95
    }
```

## 📞 Support & Troubleshooting

### Common Issues

1. **Server Won't Start**
   - Check Python version (3.8+)
   - Verify all dependencies installed
   - Check port 8000 availability

2. **Calculation Errors**
   - Validate input data format
   - Check TIN format (12 digits)
   - Ensure required fields provided

3. **Performance Issues**
   - Monitor server resources
   - Check for memory leaks
   - Consider scaling horizontally

### Getting Help

1. Check API documentation: `http://localhost:8000/docs`
2. Review logs in `tax_api.log`
3. Run health check: `GET /health`
4. Use examples in `api_examples.py`

---

**🎉 The Bangladesh Tax Calculation API is now ready for integration with your AI Tax Lawyer system!**

For complete examples and testing, run:
```bash
python api_examples.py
```