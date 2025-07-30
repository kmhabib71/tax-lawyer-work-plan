#!/usr/bin/env python3
"""
Bangladesh Tax Calculation API Backend
=====================================

FastAPI backend for the comprehensive Bangladesh Tax Calculation Engine 2024-25.
Provides RESTful endpoints for tax calculations, validation, and analysis.

Features:
- Complete integration with comprehensive_tax_engine_2024_25.py
- Pydantic models for data validation
- Comprehensive error handling
- Audit logging
- API documentation
- Health checks and monitoring
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional, Union
from decimal import Decimal, InvalidOperation
from datetime import datetime
import logging
import json
import os
import sys
import traceback
from contextlib import asynccontextmanager

# Import our comprehensive tax engine
from comprehensive_tax_engine_2024_25 import (
    ComprehensiveTaxEngine,
    TaxpayerProfile,
    IncomeDetails,
    InvestmentRebate,
    LifestyleExpenses,
    AssetsLiabilities,
    TaxPayments,
    TaxpayerCategory,
    IncomeSource,
    LocationCategory,
    SpecialStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tax_api.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global tax engine instance
tax_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global tax_engine
    logger.info("Initializing Bangladesh Tax Calculation API Backend...")
    
    try:
        # Initialize the comprehensive tax engine
        circular_data_path = "income_tax_circular_2024_25_complete.json"
        if os.path.exists(circular_data_path):
            tax_engine = ComprehensiveTaxEngine(circular_data_path)
            logger.info("Tax engine initialized successfully")
        else:
            tax_engine = ComprehensiveTaxEngine()
            logger.warning("Circular data file not found, using default configuration")
        
        logger.info("API backend startup completed")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize tax engine: {str(e)}")
        raise
    finally:
        logger.info("API backend shutdown completed")

# Create FastAPI application
app = FastAPI(
    title="Bangladesh Tax Calculation API",
    description="Comprehensive tax calculation API for Bangladesh Income Tax Act 2024-25",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred during processing",
            "timestamp": datetime.now().isoformat()
        }
    )

# Dependency to get tax engine
def get_tax_engine() -> ComprehensiveTaxEngine:
    if tax_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Tax calculation engine not available"
        )
    return tax_engine

# Pydantic Models for API
class DecimalField(BaseModel):
    """Custom decimal field with validation"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, (int, float, str)):
            try:
                return Decimal(str(v))
            except InvalidOperation:
                raise ValueError(f"Invalid decimal value: {v}")
        elif isinstance(v, Decimal):
            return v
        else:
            raise ValueError(f"Invalid decimal type: {type(v)}")

class TaxpayerProfileRequest(BaseModel):
    """API model for taxpayer profile"""
    name: str = Field(..., min_length=1, max_length=200)
    tin: str = Field(..., min_length=12, max_length=12, regex=r'^\d{12}$')
    nid: str = Field(..., min_length=10, max_length=17)
    category: str = Field(..., description="Taxpayer category")
    age: int = Field(..., ge=1, le=150)
    gender: str = Field(..., description="Gender: male, female, third_gender")
    marital_status: str = Field(..., description="Marital status")
    location: str = Field(..., description="Location category")
    residential_status: str = Field(default="resident")
    
    # Special status
    special_statuses: List[str] = Field(default=[])
    disability_type: Optional[str] = None
    disability_percentage: Optional[float] = Field(None, ge=0, le=100)
    
    # Professional information
    profession: Optional[str] = None
    employer_name: Optional[str] = None
    employer_bin: Optional[str] = None
    business_type: Optional[str] = None
    industry_sector: Optional[str] = None
    
    # Company-specific
    company_type: Optional[str] = None
    listing_status: Optional[str] = None
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = [cat.value for cat in TaxpayerCategory]
        if v not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {valid_categories}")
        return v
    
    @validator('location')
    def validate_location(cls, v):
        valid_locations = [loc.value for loc in LocationCategory]
        if v not in valid_locations:
            raise ValueError(f"Invalid location. Must be one of: {valid_locations}")
        return v
    
    @validator('special_statuses')
    def validate_special_statuses(cls, v):
        valid_statuses = [status.value for status in SpecialStatus]
        for status in v:
            if status not in valid_statuses:
                raise ValueError(f"Invalid special status: {status}. Must be one of: {valid_statuses}")
        return v

class IncomeDetailsRequest(BaseModel):
    """API model for income details"""
    # Employment Income
    basic_salary: float = Field(default=0, ge=0)
    house_rent_allowance: float = Field(default=0, ge=0)
    medical_allowance: float = Field(default=0, ge=0)
    conveyance_allowance: float = Field(default=0, ge=0)
    other_allowances: float = Field(default=0, ge=0)
    bonus: float = Field(default=0, ge=0)
    overtime: float = Field(default=0, ge=0)
    pension: float = Field(default=0, ge=0)
    gratuity: float = Field(default=0, ge=0)
    
    # Rental Income
    house_property_rent: float = Field(default=0, ge=0)
    commercial_property_rent: float = Field(default=0, ge=0)
    land_rent: float = Field(default=0, ge=0)
    
    # Agriculture Income
    agricultural_income: float = Field(default=0, ge=0)
    livestock_income: float = Field(default=0, ge=0)
    fisheries_income: float = Field(default=0, ge=0)
    poultry_income: float = Field(default=0, ge=0)
    
    # Business Income
    business_income: float = Field(default=0, ge=0)
    trading_income: float = Field(default=0, ge=0)
    manufacturing_income: float = Field(default=0, ge=0)
    service_income: float = Field(default=0, ge=0)
    
    # Capital Gains
    share_capital_gains: float = Field(default=0, ge=0)
    property_capital_gains: float = Field(default=0, ge=0)
    securities_capital_gains: float = Field(default=0, ge=0)
    
    # Financial Assets
    bank_interest: float = Field(default=0, ge=0)
    dividend_income: float = Field(default=0, ge=0)
    prize_income: float = Field(default=0, ge=0)
    
    # Other Sources
    royalty_income: float = Field(default=0, ge=0)
    professional_fees: float = Field(default=0, ge=0)
    commission_income: float = Field(default=0, ge=0)
    other_income: float = Field(default=0, ge=0)
    
    # Firm/AOP Share
    firm_share: float = Field(default=0, ge=0)
    aop_share: float = Field(default=0, ge=0)
    
    # Spouse/Minor Income
    spouse_income: float = Field(default=0, ge=0)
    minor_income: float = Field(default=0, ge=0)
    
    # Foreign Income
    foreign_employment: float = Field(default=0, ge=0)
    foreign_business: float = Field(default=0, ge=0)
    foreign_other: float = Field(default=0, ge=0)

class InvestmentRebateRequest(BaseModel):
    """API model for investment rebate details"""
    # Life Insurance & Pension
    life_insurance_premium: float = Field(default=0, ge=0)
    dps_contribution: float = Field(default=0, ge=0)
    universal_pension: float = Field(default=0, ge=0)
    
    # Government Securities
    sanchayapatra: float = Field(default=0, ge=0)
    savings_certificate: float = Field(default=0, ge=0)
    treasury_bond: float = Field(default=0, ge=0)
    
    # Stock Market
    listed_securities: float = Field(default=0, ge=0)
    mutual_fund_units: float = Field(default=0, ge=0)
    etf_investment: float = Field(default=0, ge=0)
    
    # Provident Funds
    gpf_contribution: float = Field(default=0, ge=0)
    rpf_contribution: float = Field(default=0, ge=0)
    superannuation_fund: float = Field(default=0, ge=0)
    
    # Others
    benevolent_fund: float = Field(default=0, ge=0)
    group_insurance: float = Field(default=0, ge=0)
    zakat_fund: float = Field(default=0, ge=0)
    charitable_donation: float = Field(default=0, ge=0)

class LifestyleExpensesRequest(BaseModel):
    """API model for lifestyle expenses"""
    # Basic Living
    food_clothing: float = Field(default=0, ge=0)
    accommodation: float = Field(default=0, ge=0)
    transportation: float = Field(default=0, ge=0)
    
    # Education & Health
    education_expenses: float = Field(default=0, ge=0)
    medical_expenses: float = Field(default=0, ge=0)
    
    # Utilities
    electricity_gas: float = Field(default=0, ge=0)
    telephone_internet: float = Field(default=0, ge=0)
    
    # Entertainment & Others
    entertainment: float = Field(default=0, ge=0)
    travel_vacation: float = Field(default=0, ge=0)
    festival_expenses: float = Field(default=0, ge=0)
    other_expenses: float = Field(default=0, ge=0)

class AssetsLiabilitiesRequest(BaseModel):
    """API model for assets and liabilities"""
    # Business Assets
    business_capital: float = Field(default=0, ge=0)
    business_property: float = Field(default=0, ge=0)
    business_equipment: float = Field(default=0, ge=0)
    
    # Personal Assets
    house_property: float = Field(default=0, ge=0)
    land_property: float = Field(default=0, ge=0)
    motor_vehicle: float = Field(default=0, ge=0)
    gold_jewelry: float = Field(default=0, ge=0)
    
    # Financial Assets
    bank_deposits: float = Field(default=0, ge=0)
    share_securities: float = Field(default=0, ge=0)
    savings_certificates: float = Field(default=0, ge=0)
    other_deposits: float = Field(default=0, ge=0)
    
    # Liabilities
    house_building_loan: float = Field(default=0, ge=0)
    motor_vehicle_loan: float = Field(default=0, ge=0)
    other_loans: float = Field(default=0, ge=0)
    business_liabilities: float = Field(default=0, ge=0)

class TaxPaymentsRequest(BaseModel):
    """API model for tax payments"""
    # Source Tax (TDS)
    salary_tds: float = Field(default=0, ge=0)
    rent_tds: float = Field(default=0, ge=0)
    contractor_tds: float = Field(default=0, ge=0)
    import_tds: float = Field(default=0, ge=0)
    other_tds: float = Field(default=0, ge=0)
    
    # Advance Tax
    advance_tax_paid: float = Field(default=0, ge=0)
    
    # Adjustment
    previous_refund: float = Field(default=0, ge=0)
    previous_due: float = Field(default=0, ge=0)

class TaxCalculationRequest(BaseModel):
    """Complete tax calculation request"""
    taxpayer: TaxpayerProfileRequest
    income: IncomeDetailsRequest
    investments: InvestmentRebateRequest = Field(default_factory=InvestmentRebateRequest)
    lifestyle: LifestyleExpensesRequest = Field(default_factory=LifestyleExpensesRequest)
    assets: AssetsLiabilitiesRequest = Field(default_factory=AssetsLiabilitiesRequest)
    payments: TaxPaymentsRequest = Field(default_factory=TaxPaymentsRequest)

class TaxCalculationResponse(BaseModel):
    """Tax calculation response"""
    success: bool
    calculation_id: str
    timestamp: str
    
    # Input summary
    taxpayer_name: str
    taxpayer_category: str
    total_income: float
    
    # Tax calculation results
    taxable_income: float
    gross_tax: float
    net_tax_after_rebate: float
    minimum_tax: float
    tax_payable: float
    total_surcharge: float
    total_amount_payable: float
    
    # Detailed breakdown
    exemptions: Dict[str, Any]
    rebates: Dict[str, Any]
    surcharges: Dict[str, Any]
    payments_summary: Dict[str, Any]
    
    # Final payment
    refund_or_payable: float
    payment_status: str
    
    # Audit trail
    calculation_steps: List[Dict[str, Any]]
    warnings: List[str]
    recommendations: List[str]

# API Endpoints

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Bangladesh Tax Calculation API",
        "version": "1.0.0",
        "description": "Comprehensive tax calculation for Bangladesh Income Tax Act 2024-25",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "calculate": "/calculate-tax",
            "validate": "/validate-taxpayer",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health", response_model=Dict[str, Any])
async def health_check(engine: ComprehensiveTaxEngine = Depends(get_tax_engine)):
    """Health check endpoint"""
    try:
        # Test basic engine functionality
        test_result = engine.log_calculation("Health check", {"status": "testing"})
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "tax_engine": "operational",
            "database": "loaded" if hasattr(engine, 'circular_data') else "default",
            "version": "2024-25"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Helper functions to convert API models to engine models
def convert_taxpayer_profile(data: TaxpayerProfileRequest) -> TaxpayerProfile:
    """Convert API taxpayer model to engine model"""
    special_statuses = [SpecialStatus(status) for status in data.special_statuses]
    
    return TaxpayerProfile(
        name=data.name,
        tin=data.tin,
        nid=data.nid,
        category=TaxpayerCategory(data.category),
        age=data.age,
        gender=data.gender,
        marital_status=data.marital_status,
        location=LocationCategory(data.location),
        residential_status=data.residential_status,
        special_statuses=special_statuses,
        disability_type=data.disability_type,
        disability_percentage=Decimal(str(data.disability_percentage)) if data.disability_percentage else None,
        profession=data.profession,
        employer_name=data.employer_name,
        employer_bin=data.employer_bin,
        business_type=data.business_type,
        industry_sector=data.industry_sector,
        company_type=data.company_type,
        listing_status=data.listing_status
    )

def convert_income_details(data: IncomeDetailsRequest) -> IncomeDetails:
    """Convert API income model to engine model"""
    return IncomeDetails(
        # Employment Income
        basic_salary=Decimal(str(data.basic_salary)),
        house_rent_allowance=Decimal(str(data.house_rent_allowance)),
        medical_allowance=Decimal(str(data.medical_allowance)),
        conveyance_allowance=Decimal(str(data.conveyance_allowance)),
        other_allowances=Decimal(str(data.other_allowances)),
        bonus=Decimal(str(data.bonus)),
        overtime=Decimal(str(data.overtime)),
        pension=Decimal(str(data.pension)),
        gratuity=Decimal(str(data.gratuity)),
        
        # Rental Income
        house_property_rent=Decimal(str(data.house_property_rent)),
        commercial_property_rent=Decimal(str(data.commercial_property_rent)),
        land_rent=Decimal(str(data.land_rent)),
        
        # Agriculture Income
        agricultural_income=Decimal(str(data.agricultural_income)),
        livestock_income=Decimal(str(data.livestock_income)),
        fisheries_income=Decimal(str(data.fisheries_income)),
        poultry_income=Decimal(str(data.poultry_income)),
        
        # Business Income
        business_income=Decimal(str(data.business_income)),
        trading_income=Decimal(str(data.trading_income)),
        manufacturing_income=Decimal(str(data.manufacturing_income)),
        service_income=Decimal(str(data.service_income)),
        
        # Capital Gains
        share_capital_gains=Decimal(str(data.share_capital_gains)),
        property_capital_gains=Decimal(str(data.property_capital_gains)),
        securities_capital_gains=Decimal(str(data.securities_capital_gains)),
        
        # Financial Assets
        bank_interest=Decimal(str(data.bank_interest)),
        dividend_income=Decimal(str(data.dividend_income)),
        prize_income=Decimal(str(data.prize_income)),
        
        # Other Sources
        royalty_income=Decimal(str(data.royalty_income)),
        professional_fees=Decimal(str(data.professional_fees)),
        commission_income=Decimal(str(data.commission_income)),
        other_income=Decimal(str(data.other_income)),
        
        # Firm/AOP Share
        firm_share=Decimal(str(data.firm_share)),
        aop_share=Decimal(str(data.aop_share)),
        
        # Spouse/Minor Income
        spouse_income=Decimal(str(data.spouse_income)),
        minor_income=Decimal(str(data.minor_income)),
        
        # Foreign Income
        foreign_employment=Decimal(str(data.foreign_employment)),
        foreign_business=Decimal(str(data.foreign_business)),
        foreign_other=Decimal(str(data.foreign_other))
    )

def convert_investment_rebate(data: InvestmentRebateRequest) -> InvestmentRebate:
    """Convert API investment model to engine model"""
    return InvestmentRebate(
        # Life Insurance & Pension
        life_insurance_premium=Decimal(str(data.life_insurance_premium)),
        dps_contribution=Decimal(str(data.dps_contribution)),
        universal_pension=Decimal(str(data.universal_pension)),
        
        # Government Securities
        sanchayapatra=Decimal(str(data.sanchayapatra)),
        savings_certificate=Decimal(str(data.savings_certificate)),
        treasury_bond=Decimal(str(data.treasury_bond)),
        
        # Stock Market
        listed_securities=Decimal(str(data.listed_securities)),
        mutual_fund_units=Decimal(str(data.mutual_fund_units)),
        etf_investment=Decimal(str(data.etf_investment)),
        
        # Provident Funds
        gpf_contribution=Decimal(str(data.gpf_contribution)),
        rpf_contribution=Decimal(str(data.rpf_contribution)),
        superannuation_fund=Decimal(str(data.superannuation_fund)),
        
        # Others
        benevolent_fund=Decimal(str(data.benevolent_fund)),
        group_insurance=Decimal(str(data.group_insurance)),
        zakat_fund=Decimal(str(data.zakat_fund)),
        charitable_donation=Decimal(str(data.charitable_donation))
    )

def convert_lifestyle_expenses(data: LifestyleExpensesRequest) -> LifestyleExpenses:
    """Convert API lifestyle model to engine model"""
    return LifestyleExpenses(
        # Basic Living
        food_clothing=Decimal(str(data.food_clothing)),
        accommodation=Decimal(str(data.accommodation)),
        transportation=Decimal(str(data.transportation)),
        
        # Education & Health
        education_expenses=Decimal(str(data.education_expenses)),
        medical_expenses=Decimal(str(data.medical_expenses)),
        
        # Utilities
        electricity_gas=Decimal(str(data.electricity_gas)),
        telephone_internet=Decimal(str(data.telephone_internet)),
        
        # Entertainment & Others
        entertainment=Decimal(str(data.entertainment)),
        travel_vacation=Decimal(str(data.travel_vacation)),
        festival_expenses=Decimal(str(data.festival_expenses)),
        other_expenses=Decimal(str(data.other_expenses))
    )

def convert_assets_liabilities(data: AssetsLiabilitiesRequest) -> AssetsLiabilities:
    """Convert API assets model to engine model"""
    return AssetsLiabilities(
        # Business Assets
        business_capital=Decimal(str(data.business_capital)),
        business_property=Decimal(str(data.business_property)),
        business_equipment=Decimal(str(data.business_equipment)),
        
        # Personal Assets
        house_property=Decimal(str(data.house_property)),
        land_property=Decimal(str(data.land_property)),
        motor_vehicle=Decimal(str(data.motor_vehicle)),
        gold_jewelry=Decimal(str(data.gold_jewelry)),
        
        # Financial Assets
        bank_deposits=Decimal(str(data.bank_deposits)),
        share_securities=Decimal(str(data.share_securities)),
        savings_certificates=Decimal(str(data.savings_certificates)),
        other_deposits=Decimal(str(data.other_deposits)),
        
        # Liabilities
        house_building_loan=Decimal(str(data.house_building_loan)),
        motor_vehicle_loan=Decimal(str(data.motor_vehicle_loan)),
        other_loans=Decimal(str(data.other_loans)),
        business_liabilities=Decimal(str(data.business_liabilities))
    )

def convert_tax_payments(data: TaxPaymentsRequest) -> TaxPayments:
    """Convert API payments model to engine model"""
    return TaxPayments(
        # Source Tax (TDS)
        salary_tds=Decimal(str(data.salary_tds)),
        rent_tds=Decimal(str(data.rent_tds)),
        contractor_tds=Decimal(str(data.contractor_tds)),
        import_tds=Decimal(str(data.import_tds)),
        other_tds=Decimal(str(data.other_tds)),
        
        # Advance Tax
        advance_tax_paid=Decimal(str(data.advance_tax_paid)),
        
        # Adjustment
        previous_refund=Decimal(str(data.previous_refund)),
        previous_due=Decimal(str(data.previous_due))
    )

def decimal_to_float(value) -> float:
    """Convert Decimal to float for JSON serialization"""
    if isinstance(value, Decimal):
        return float(value)
    return value

def convert_result_to_response(result: Dict[str, Any], request_data: TaxCalculationRequest) -> TaxCalculationResponse:
    """Convert engine result to API response"""
    import uuid
    
    # Calculate refund or additional payment
    total_payments = (
        float(result.get('total_payments', 0)) + 
        float(result.get('previous_refund', 0)) - 
        float(result.get('previous_due', 0))
    )
    total_payable = float(result.get('total_amount_payable', 0))
    refund_or_payable = total_payable - total_payments
    
    payment_status = "refund" if refund_or_payable < 0 else "payable" if refund_or_payable > 0 else "settled"
    
    return TaxCalculationResponse(
        success=True,
        calculation_id=str(uuid.uuid4()),
        timestamp=datetime.now().isoformat(),
        
        # Input summary
        taxpayer_name=request_data.taxpayer.name,
        taxpayer_category=request_data.taxpayer.category,
        total_income=decimal_to_float(result.get('total_income', 0)),
        
        # Tax calculation results
        taxable_income=decimal_to_float(result.get('taxable_income', 0)),
        gross_tax=decimal_to_float(result.get('gross_tax', 0)),
        net_tax_after_rebate=decimal_to_float(result.get('net_tax_after_rebate', 0)),
        minimum_tax=decimal_to_float(result.get('minimum_tax', 0)),
        tax_payable=decimal_to_float(result.get('tax_payable', 0)),
        total_surcharge=decimal_to_float(result.get('total_surcharge', 0)),
        total_amount_payable=total_payable,
        
        # Detailed breakdown
        exemptions=result.get('exemptions', {}),
        rebates=result.get('rebates', {}),
        surcharges=result.get('surcharges', {}),
        payments_summary=result.get('payments_summary', {}),
        
        # Final payment
        refund_or_payable=abs(refund_or_payable),
        payment_status=payment_status,
        
        # Audit trail
        calculation_steps=result.get('calculation_steps', []),
        warnings=result.get('warnings', []),
        recommendations=result.get('recommendations', [])
    )

@app.post("/calculate-tax", response_model=TaxCalculationResponse)
async def calculate_tax(
    request: TaxCalculationRequest,
    background_tasks: BackgroundTasks,
    engine: ComprehensiveTaxEngine = Depends(get_tax_engine)
):
    """
    Calculate comprehensive tax for a taxpayer
    
    This endpoint performs a complete tax calculation including:
    - Income from all sources (employment, business, rental, etc.)
    - Exemptions based on taxpayer profile
    - Investment rebates
    - Minimum tax calculations
    - Surcharges (wealth, environmental, etc.)
    - Final tax payable or refund amount
    """
    try:
        logger.info(f"Starting tax calculation for taxpayer: {request.taxpayer.name}")
        
        # Convert API models to engine models
        taxpayer = convert_taxpayer_profile(request.taxpayer)
        income = convert_income_details(request.income)
        investments = convert_investment_rebate(request.investments)
        lifestyle = convert_lifestyle_expenses(request.lifestyle)
        assets = convert_assets_liabilities(request.assets)
        payments = convert_tax_payments(request.payments)
        
        # Perform comprehensive tax calculation
        result = engine.calculate_comprehensive_tax(
            taxpayer=taxpayer,
            income=income,
            investments=investments,
            lifestyle=lifestyle,
            assets=assets,
            payments=payments
        )
        
        # Convert result to API response
        response = convert_result_to_response(result, request)
        
        # Log successful calculation
        logger.info(f"Tax calculation completed for {request.taxpayer.name}. "
                   f"Total income: ₹{response.total_income:,.2f}, "
                   f"Tax payable: ₹{response.tax_payable:,.2f}")
        
        # Background task for audit logging
        background_tasks.add_task(
            log_calculation_audit,
            request.taxpayer.tin,
            request.taxpayer.name,
            response.calculation_id,
            response.total_income,
            response.tax_payable
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in tax calculation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in tax calculation: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="Tax calculation failed due to internal error"
        )

async def log_calculation_audit(tin: str, name: str, calculation_id: str, total_income: float, tax_payable: float):
    """Background task for audit logging"""
    try:
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "calculation_id": calculation_id,
            "taxpayer_tin": tin,
            "taxpayer_name": name,
            "total_income": total_income,
            "tax_payable": tax_payable,
            "api_version": "1.0.0"
        }
        
        # Log to file (in production, this could be a database)
        with open("tax_calculation_audit.log", "a") as f:
            f.write(json.dumps(audit_entry) + "\n")
            
        logger.info(f"Audit logged for calculation {calculation_id}")
        
    except Exception as e:
        logger.error(f"Failed to log audit entry: {str(e)}")

@app.post("/validate-taxpayer", response_model=Dict[str, Any])
async def validate_taxpayer(
    taxpayer_data: TaxpayerProfileRequest,
    engine: ComprehensiveTaxEngine = Depends(get_tax_engine)
):
    """
    Validate taxpayer profile data
    
    Performs comprehensive validation including:
    - TIN format validation
    - Category-specific validations
    - Special status eligibility
    - Data consistency checks
    """
    try:
        logger.info(f"Validating taxpayer profile: {taxpayer_data.name}")
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "taxpayer_info": {
                "name": taxpayer_data.name,
                "tin": taxpayer_data.tin,
                "category": taxpayer_data.category,
                "location": taxpayer_data.location
            }
        }
        
        # TIN validation
        if not re.match(r'^\d{12}$', taxpayer_data.tin):
            validation_results["errors"].append("TIN must be exactly 12 digits")
            validation_results["valid"] = False
        
        # Age validation for special statuses
        if SpecialStatus.SENIOR_CITIZEN.value in taxpayer_data.special_statuses and taxpayer_data.age < 65:
            validation_results["errors"].append("Senior citizen status requires age 65 or above")
            validation_results["valid"] = False
        
        # Category-specific validations
        if taxpayer_data.category == TaxpayerCategory.COMPANY.value:
            if not taxpayer_data.company_type:
                validation_results["warnings"].append("Company type should be specified for companies")
        
        # Disability validation
        if SpecialStatus.DISABLED_PERSON.value in taxpayer_data.special_statuses:
            if not taxpayer_data.disability_type:
                validation_results["warnings"].append("Disability type should be specified")
            if not taxpayer_data.disability_percentage or taxpayer_data.disability_percentage < 1:
                validation_results["warnings"].append("Disability percentage should be specified")
        
        # Professional information validation
        if taxpayer_data.category == TaxpayerCategory.INDIVIDUAL.value:
            if not taxpayer_data.profession:
                validation_results["warnings"].append("Profession information recommended for individuals")
        
        logger.info(f"Taxpayer validation completed: {validation_results['valid']}")
        return validation_results
        
    except Exception as e:
        logger.error(f"Error in taxpayer validation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Validation failed due to internal error"
        )

@app.get("/tax-info", response_model=Dict[str, Any])
async def get_tax_info():
    """
    Get tax system information and rates
    
    Returns current tax rates, exemption limits, and other tax information
    """
    try:
        tax_info = {
            "tax_year": "2024-25",
            "individual_tax_slabs": [
                {"range": "0 - 350,000", "rate": "0%"},
                {"range": "350,001 - 450,000", "rate": "5%"},
                {"range": "450,001 - 750,000", "rate": "10%"},
                {"range": "750,001 - 1,150,000", "rate": "15%"},
                {"range": "1,150,001 - 1,650,000", "rate": "20%"},
                {"range": "Above 1,650,000", "rate": "25%"}
            ],
            "company_tax_rates": {
                "publicly_traded": "25%",
                "private_limited": "27.5%",
                "bank_insurance": "40%",
                "tobacco": "45%"
            },
            "special_exemptions": {
                "female": "25,000 additional",
                "senior_citizen": "50,000 additional", 
                "disabled_physical": "100,000 additional",
                "disabled_intellectual": "125,000 additional",
                "freedom_fighter": "75,000 additional"
            },
            "investment_rebate": {
                "rate": "15%",
                "maximum_limit": "15% of gross tax or investment amount limits"
            },
            "surcharges": {
                "wealth_surcharge": "10-25% based on net worth",
                "environmental_surcharge": "1% for companies"
            }
        }
        
        return tax_info
        
    except Exception as e:
        logger.error(f"Error retrieving tax info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve tax information"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "tax_api_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True
    )