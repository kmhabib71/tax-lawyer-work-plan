#!/usr/bin/env python3
"""
Bangladesh Tax Calculation API - Usage Examples
==============================================

This file contains comprehensive examples for using the Tax Calculation API.
Examples cover all major scenarios including individuals, companies, and special cases.

Usage:
    python api_examples.py

Requirements:
    - API server running on http://localhost:8000
    - requests library installed
"""

import requests
import json
from typing import Dict, Any
import time

# API base URL
BASE_URL = "http://localhost:8000"

def make_request(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make API request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return {"error": str(e)}

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def print_response(response: Dict[str, Any], title: str = "Response"):
    """Pretty print API response"""
    print(f"\n{title}:")
    print(json.dumps(response, indent=2, default=str))

# Example 1: Basic Individual Taxpayer
def example_basic_individual():
    """Example: Basic individual with salary income"""
    print_section("Example 1: Basic Individual Taxpayer")
    
    request_data = {
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
    
    response = make_request("/calculate-tax", "POST", request_data)
    print_response(response)
    
    if response.get("success"):
        print(f"\nSummary for {request_data['taxpayer']['name']}:")
        print(f"Total Income: ₹{response['total_income']:,.2f}")
        print(f"Taxable Income: ₹{response['taxable_income']:,.2f}")
        print(f"Gross Tax: ₹{response['gross_tax']:,.2f}")
        print(f"Tax After Rebate: ₹{response['net_tax_after_rebate']:,.2f}")
        print(f"Final Tax Payable: ₹{response['tax_payable']:,.2f}")

# Example 2: Female Individual with Special Benefits
def example_female_individual():
    """Example: Female individual with special exemptions"""
    print_section("Example 2: Female Individual with Special Benefits")
    
    request_data = {
        "taxpayer": {
            "name": "Fatima Rahman",
            "tin": "987654321098",
            "nid": "9876543210987",
            "category": "individual",
            "age": 28,
            "gender": "female",
            "marital_status": "single",
            "location": "chittagong_city",
            "special_statuses": ["female"],
            "profession": "Doctor"
        },
        "income": {
            "basic_salary": 600000,
            "house_rent_allowance": 150000,
            "medical_allowance": 30000,
            "professional_fees": 100000
        },
        "investments": {
            "life_insurance_premium": 40000,
            "government_securities": 60000,
            "mutual_fund": 80000
        }
    }
    
    response = make_request("/calculate-tax", "POST", request_data)
    print_response(response)
    
    if response.get("success"):
        print(f"\nSummary for {request_data['taxpayer']['name']}:")
        print(f"Total Income: ₹{response['total_income']:,.2f}")
        print(f"Tax Payable: ₹{response['tax_payable']:,.2f}")
        print(f"Special Status Benefits Applied: Female (+₹25,000 exemption)")

# Example 3: Senior Citizen with Disability
def example_senior_disabled():
    """Example: Senior citizen with disability benefits"""
    print_section("Example 3: Senior Citizen with Disability")
    
    request_data = {
        "taxpayer": {
            "name": "Abdul Karim",
            "tin": "111222333444",
            "nid": "1112223334445",
            "category": "individual",
            "age": 70,
            "gender": "male",
            "marital_status": "married",
            "location": "other_area",
            "special_statuses": ["senior_citizen", "disabled_person"],
            "disability_type": "physical",
            "disability_percentage": 60
        },
        "income": {
            "pension": 400000,
            "bank_interest": 80000,
            "rental_income": 120000
        },
        "investments": {
            "life_insurance_premium": 20000,
            "savings_certificates": 150000
        }
    }
    
    response = make_request("/calculate-tax", "POST", request_data)
    print_response(response)

# Example 4: Company Tax Calculation
def example_company():
    """Example: Private limited company"""
    print_section("Example 4: Private Limited Company")
    
    request_data = {
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
    
    response = make_request("/calculate-tax", "POST", request_data)
    print_response(response)

# Example 5: Complex Business Owner
def example_business_owner():
    """Example: Individual with multiple income sources"""
    print_section("Example 5: Complex Business Owner")
    
    request_data = {
        "taxpayer": {
            "name": "Mohammad Ali",
            "tin": "999888777666",
            "nid": "9998887776666",
            "category": "individual",
            "age": 45,
            "gender": "male",
            "marital_status": "married",
            "location": "dhaka_city",
            "profession": "Business Owner"
        },
        "income": {
            "business_income": 1500000,
            "rental_income": 400000,
            "agricultural_income": 200000,
            "bank_interest": 150000,
            "dividend_income": 100000,
            "capital_gains": 300000
        },
        "investments": {
            "life_insurance_premium": 100000,
            "stock_purchase": 200000,
            "government_securities": 150000,
            "mutual_fund": 80000
        },
        "assets": {
            "house_property": 5000000,
            "business_capital": 3000000,
            "bank_deposits": 1000000,
            "motor_vehicle": 800000
        },
        "lifestyle": {
            "food_clothing": 300000,
            "accommodation": 200000,
            "transportation": 150000,
            "education_expenses": 100000
        }
    }
    
    response = make_request("/calculate-tax", "POST", request_data)
    print_response(response)

# Example 6: Taxpayer Validation
def example_validation():
    """Example: Taxpayer profile validation"""
    print_section("Example 6: Taxpayer Profile Validation")
    
    # Valid taxpayer
    valid_taxpayer = {
        "name": "Rashida Begum",
        "tin": "123456789012",
        "nid": "1234567890123",
        "category": "individual",
        "age": 30,
        "gender": "female",
        "marital_status": "married",
        "location": "dhaka_city",
        "special_statuses": ["female"]
    }
    
    response = make_request("/validate-taxpayer", "POST", valid_taxpayer)
    print_response(response, "Valid Taxpayer Validation")
    
    # Invalid taxpayer (invalid TIN)
    invalid_taxpayer = {
        "name": "Test User",
        "tin": "12345",  # Invalid TIN
        "nid": "1234567890123",
        "category": "individual",
        "age": 60,
        "gender": "male",
        "marital_status": "single",
        "location": "dhaka_city",
        "special_statuses": ["senior_citizen"]  # Age doesn't match
    }
    
    response = make_request("/validate-taxpayer", "POST", invalid_taxpayer)
    print_response(response, "Invalid Taxpayer Validation")

# Example 7: Tax Information
def example_tax_info():
    """Example: Get tax system information"""
    print_section("Example 7: Tax System Information")
    
    response = make_request("/tax-info")
    print_response(response)

# Example 8: Health Check
def example_health_check():
    """Example: API health check"""
    print_section("Example 8: API Health Check")
    
    response = make_request("/health")
    print_response(response)

# Performance testing
def performance_test():
    """Test API performance with multiple requests"""
    print_section("Performance Test: Multiple Tax Calculations")
    
    # Simple test data
    test_data = {
        "taxpayer": {
            "name": "Performance Test",
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
    
    num_requests = 10
    start_time = time.time()
    
    successful_requests = 0
    for i in range(num_requests):
        response = make_request("/calculate-tax", "POST", test_data)
        if response.get("success"):
            successful_requests += 1
        print(f"Request {i+1}/{num_requests} completed")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\nPerformance Results:")
    print(f"Total requests: {num_requests}")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {num_requests - successful_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per request: {total_time/num_requests:.2f} seconds")
    print(f"Requests per second: {num_requests/total_time:.2f}")

def main():
    """Run all examples"""
    print("Bangladesh Tax Calculation API - Usage Examples")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = make_request("/")
        if "error" in response:
            print("❌ API server is not running. Please start the server first:")
            print("   python tax_api_backend.py")
            return
        print("✅ API server is running")
    except:
        print("❌ Cannot connect to API server. Please start the server first:")
        print("   python tax_api_backend.py")
        return
    
    # Run examples
    try:
        example_health_check()
        example_tax_info()
        example_basic_individual()
        example_female_individual()
        example_senior_disabled()
        example_company()
        example_business_owner()
        example_validation()
        
        # Optional performance test
        print("\n" + "="*60)
        run_perf = input("Run performance test? (y/n): ").lower().strip()
        if run_perf == 'y':
            performance_test()
        
        print("\n🎉 All examples completed successfully!")
        print("\nAPI Documentation available at: http://localhost:8000/docs")
        print("Alternative docs at: http://localhost:8000/redoc")
        
    except KeyboardInterrupt:
        print("\n⚠️ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")

if __name__ == "__main__":
    main()