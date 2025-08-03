"""
Tax Rules Engine Package
========================

Core rule-based calculation engine for Bangladesh tax law system.
Processes legal data to provide accurate tax calculations and validations.

Version: 1.0.0
Author: AI Tax Lawyer Bangladesh Project
"""

__version__ = "1.0.0"
__author__ = "AI Tax Lawyer Bangladesh Project"

from .core.rule_engine import RuleEngine
from .core.calculation_engine import CalculationEngine
from .core.validation_engine import ValidationEngine

__all__ = [
    'RuleEngine',
    'CalculationEngine', 
    'ValidationEngine'
]