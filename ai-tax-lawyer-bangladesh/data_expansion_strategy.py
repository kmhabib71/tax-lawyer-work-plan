#!/usr/bin/env python3
"""
Data Expansion Strategy - Week 1 Implementation
Incremental expansion plan for remaining 1,376 legal documents
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import re
from collections import defaultdict, Counter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataExpansionStrategy:
    """Strategic data expansion manager for legal documents"""
    
    def __init__(self, data_directory: str = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap"):
        self.data_directory = Path(data_directory)
        self.legal_docs_path = self.data_directory / "ai-tax-lawyer-bangladesh" / "data" / "legal_documents"
        self.processed_data_path = self.data_directory / "ai-tax-lawyer-bangladesh" / "data" / "processed_data"
        
        # Expansion tracking
        self.current_documents = 148  # From validation
        self.target_documents = 1524  # Total available
        self.remaining_documents = self.target_documents - self.current_documents
        
        # Priority categorization
        self.priority_categories = {
            "critical": {
                "weight": 1.0,
                "description": "Essential tax laws and current regulations",
                "target_percentage": 30
            },
            "important": {
                "weight": 0.7,
                "description": "Supporting regulations and historical laws",
                "target_percentage": 40
            },
            "supplementary": {
                "weight": 0.5,
                "description": "Reference materials and archived documents",
                "target_percentage": 30
            }
        }
        
        logger.info(f"📊 Data Expansion Strategy initialized")
        logger.info(f"   Current: {self.current_documents} documents")
        logger.info(f"   Target: {self.target_documents} documents")
        logger.info(f"   Remaining: {self.remaining_documents} documents")
    
    def analyze_current_dataset(self) -> Dict[str, Any]:
        """Analyze current dataset composition and gaps"""
        analysis = {
            "total_files": 0,
            "by_category": defaultdict(int),
            "by_type": defaultdict(int),
            "by_year": defaultdict(int),
            "file_sizes": [],
            "coverage_gaps": [],
            "quality_metrics": {}
        }
        
        logger.info("🔍 Analyzing current dataset composition...")
        
        # Scan legal documents directory
        if self.legal_docs_path.exists():
            for category_dir in self.legal_docs_path.iterdir():
                if category_dir.is_dir():
                    category_name = category_dir.name
                    category_files = list(category_dir.glob("**/*"))
                    
                    analysis["by_category"][category_name] = len([f for f in category_files if f.is_file()])
                    
                    # Analyze files in category
                    for file_path in category_files:
                        if file_path.is_file():
                            analysis["total_files"] += 1
                            
                            # File type analysis
                            file_ext = file_path.suffix.lower()
                            analysis["by_type"][file_ext] += 1
                            
                            # File size analysis
                            try:
                                file_size = file_path.stat().st_size
                                analysis["file_sizes"].append(file_size)
                            except:
                                pass
                            
                            # Year extraction from filename
                            year_match = re.search(r'20\d{2}', file_path.name)
                            if year_match:
                                analysis["by_year"][year_match.group()] += 1
        
        # Calculate quality metrics
        if analysis["file_sizes"]:
            analysis["quality_metrics"] = {
                "avg_file_size_kb": sum(analysis["file_sizes"]) / len(analysis["file_sizes"]) / 1024,
                "min_file_size_kb": min(analysis["file_sizes"]) / 1024,
                "max_file_size_kb": max(analysis["file_sizes"]) / 1024,
                "total_size_mb": sum(analysis["file_sizes"]) / (1024 * 1024)
            }
        
        # Identify coverage gaps
        analysis["coverage_gaps"] = self._identify_coverage_gaps(analysis)
        
        logger.info(f"✅ Dataset analysis complete:")
        logger.info(f"   Total files: {analysis['total_files']}")
        logger.info(f"   Categories: {dict(analysis['by_category'])}")
        logger.info(f"   File types: {dict(analysis['by_type'])}")
        
        return analysis
    
    def _identify_coverage_gaps(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify gaps in legal document coverage"""
        gaps = []
        
        # Expected categories and their minimum requirements
        expected_categories = {
            "income_tax": {"min_files": 50, "priority": "critical"},
            "corporate_tax": {"min_files": 30, "priority": "critical"},
            "vat_customs": {"min_files": 40, "priority": "critical"},
            "circulars": {"min_files": 100, "priority": "important"},
            "finance_acts": {"min_files": 20, "priority": "critical"},
            "tax_ordinances": {"min_files": 15, "priority": "critical"},
            "court_decisions": {"min_files": 25, "priority": "important"},
            "administrative_orders": {"min_files": 30, "priority": "supplementary"}
        }
        
        for category, requirements in expected_categories.items():
            current_count = analysis["by_category"].get(category, 0)
            min_required = requirements["min_files"]
            priority = requirements["priority"]
            
            if current_count < min_required:
                gap = {
                    "category": category,
                    "current_files": current_count,
                    "required_files": min_required,
                    "deficit": min_required - current_count,
                    "priority": priority,
                    "urgency_score": self._calculate_urgency_score(
                        current_count, min_required, priority
                    )
                }
                gaps.append(gap)
        
        # Sort by urgency score (highest first)
        gaps.sort(key=lambda x: x["urgency_score"], reverse=True)
        
        return gaps
    
    def _calculate_urgency_score(self, current: int, required: int, priority: str) -> float:
        """Calculate urgency score for filling a gap"""
        priority_weights = {"critical": 1.0, "important": 0.7, "supplementary": 0.5}
        
        completion_ratio = current / required if required > 0 else 1.0
        urgency = (1.0 - completion_ratio) * priority_weights.get(priority, 0.5)
        
        return urgency
    
    def create_expansion_plan(self, target_timeline_weeks: int = 8) -> Dict[str, Any]:
        """Create phased expansion plan for remaining documents"""
        
        # Analyze current state
        current_analysis = self.analyze_current_dataset()
        gaps = current_analysis["coverage_gaps"]
        
        # Calculate weekly targets
        weekly_document_target = max(1, self.remaining_documents // target_timeline_weeks)
        
        expansion_plan = {
            "timeline_weeks": target_timeline_weeks,
            "weekly_target": weekly_document_target,
            "total_remaining": self.remaining_documents,
            "phases": [],
            "priority_allocation": {},
            "implementation_strategy": {}
        }
        
        logger.info(f"📋 Creating {target_timeline_weeks}-week expansion plan...")
        logger.info(f"   Weekly target: {weekly_document_target} documents")
        
        # Phase 1: Critical gaps (Weeks 1-3)
        phase1_docs = min(weekly_document_target * 3, self.remaining_documents // 2)
        expansion_plan["phases"].append({
            "phase": 1,
            "weeks": "1-3",
            "documents": phase1_docs,
            "focus": "Critical legal gaps",
            "categories": [gap["category"] for gap in gaps[:3] if gap["priority"] == "critical"],
            "success_criteria": "All critical categories meet minimum requirements"
        })
        
        # Phase 2: Important gaps (Weeks 4-6)
        phase2_docs = min(weekly_document_target * 3, 
                         self.remaining_documents - phase1_docs)
        expansion_plan["phases"].append({
            "phase": 2,
            "weeks": "4-6", 
            "documents": phase2_docs,
            "focus": "Important supporting documents",
            "categories": [gap["category"] for gap in gaps if gap["priority"] == "important"],
            "success_criteria": "70% coverage of important categories"
        })
        
        # Phase 3: Supplementary and quality improvement (Weeks 7-8)
        phase3_docs = self.remaining_documents - phase1_docs - phase2_docs
        expansion_plan["phases"].append({
            "phase": 3,
            "weeks": "7-8",
            "documents": phase3_docs,
            "focus": "Supplementary documents and quality enhancement",
            "categories": ["supplementary", "historical_documents", "reference_materials"],
            "success_criteria": "Complete target coverage with quality validation"
        })
        
        # Priority allocation strategy
        expansion_plan["priority_allocation"] = {
            "critical": {
                "percentage": 50,
                "documents": int(self.remaining_documents * 0.5),
                "focus_areas": ["current_tax_laws", "active_regulations", "finance_acts"]
            },
            "important": {
                "percentage": 35,
                "documents": int(self.remaining_documents * 0.35),
                "focus_areas": ["historical_laws", "circulars", "administrative_orders"]
            },
            "supplementary": {
                "percentage": 15,
                "documents": int(self.remaining_documents * 0.15),
                "focus_areas": ["reference_materials", "archived_documents", "precedents"]
            }
        }
        
        # Implementation strategy
        expansion_plan["implementation_strategy"] = {
            "batch_processing": {
                "batch_size": 25,
                "processing_time_per_batch": "2-3 hours",
                "quality_validation": "Required for each batch"
            },
            "automation": {
                "document_extraction": "Automated with manual verification",
                "metadata_generation": "AI-assisted with human review",
                "quality_scoring": "Automated threshold checking"
            },
            "quality_gates": {
                "minimum_file_size": "5KB",
                "text_extraction_success": "95%",
                "metadata_completeness": "90%",
                "duplicate_detection": "Automated"
            },
            "progress_tracking": {
                "daily_reports": "Automated generation",
                "weekly_reviews": "Manual assessment",
                "milestone_validation": "Comprehensive testing"
            }
        }
        
        return expansion_plan
    
    def generate_weekly_targets(self, expansion_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific weekly targets for data expansion"""
        weekly_targets = []
        
        total_weeks = expansion_plan["timeline_weeks"]
        base_weekly_target = expansion_plan["weekly_target"]
        
        for week in range(1, total_weeks + 1):
            # Determine which phase this week belongs to
            if week <= 3:
                phase = 1
                focus = "Critical legal documents"
                target_multiplier = 1.2  # Higher priority in early weeks
            elif week <= 6:
                phase = 2
                focus = "Important supporting documents"
                target_multiplier = 1.0
            else:
                phase = 3
                focus = "Supplementary and quality improvement"
                target_multiplier = 0.8  # Lower volume, higher quality focus
            
            weekly_target = int(base_weekly_target * target_multiplier)
            
            # Calculate cumulative targets
            cumulative_target = sum(
                target["documents_target"] for target in weekly_targets
            ) + weekly_target
            
            week_plan = {
                "week": week,
                "phase": phase,
                "focus": focus,
                "documents_target": weekly_target,
                "cumulative_target": cumulative_target,
                "completion_percentage": (cumulative_target / self.remaining_documents) * 100,
                "key_activities": self._get_weekly_activities(week, phase),
                "success_metrics": {
                    "documents_added": weekly_target,
                    "quality_score": ">= 85%",
                    "processing_time": "<= 4 hours",
                    "error_rate": "<= 5%"
                }
            }
            
            weekly_targets.append(week_plan)
        
        return weekly_targets
    
    def _get_weekly_activities(self, week: int, phase: int) -> List[str]:
        """Get specific activities for each week"""
        activities_map = {
            1: [
                "Priority assessment of critical tax laws",
                "Income tax documents batch processing",
                "Quality validation setup"
            ],
            2: [
                "Corporate tax regulations processing",
                "VAT/Customs documents integration",
                "Metadata enhancement automation"
            ],
            3: [
                "Finance Acts and ordinances processing",
                "Critical gaps closure validation",
                "Phase 1 completion assessment"
            ],
            4: [
                "Circulars and administrative orders",
                "Historical documents processing",
                "Cross-reference validation"
            ],
            5: [
                "Court decisions and precedents",
                "Regulatory interpretations",
                "Knowledge base optimization"
            ],
            6: [
                "Supporting documentation completion",
                "Phase 2 quality assessment",
                "Integration testing"
            ],
            7: [
                "Reference materials processing",
                "Archived documents integration",
                "Comprehensive quality review"
            ],
            8: [
                "Final document batch processing",
                "Complete system validation",
                "Expansion strategy completion"
            ]
        }
        
        return activities_map.get(week, ["Document processing", "Quality validation"])
    
    def estimate_resources_required(self, expansion_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resources required for data expansion"""
        
        total_documents = self.remaining_documents
        weekly_target = expansion_plan["weekly_target"]
        timeline_weeks = expansion_plan["timeline_weeks"]
        
        # Time estimates (in hours)
        time_per_document = {
            "extraction": 0.05,      # 3 minutes per document
            "processing": 0.1,       # 6 minutes per document  
            "validation": 0.08,      # 5 minutes per document
            "metadata": 0.07,        # 4 minutes per document
            "integration": 0.05      # 3 minutes per document
        }
        
        total_time_per_doc = sum(time_per_document.values())  # ~21 minutes per document
        
        resource_estimates = {
            "time_requirements": {
                "total_hours": total_documents * total_time_per_doc,
                "weekly_hours": weekly_target * total_time_per_doc,
                "daily_hours": (weekly_target * total_time_per_doc) / 7,
                "breakdown_per_document": time_per_document
            },
            "human_resources": {
                "data_analyst": "1 person, 20 hours/week",
                "quality_reviewer": "0.5 person, 10 hours/week", 
                "technical_coordinator": "0.25 person, 5 hours/week"
            },
            "technical_resources": {
                "processing_power": "Standard laptop sufficient",
                "storage_space": f"{(total_documents * 100) / 1024:.1f} GB estimated",
                "internet_bandwidth": "Standard broadband for downloads",
                "backup_storage": "Cloud storage recommended"
            },
            "cost_estimates": {
                "labor_cost_weekly": "35 hours * hourly_rate",
                "infrastructure_cost": "Minimal - existing systems",
                "total_timeline_cost": f"{timeline_weeks} weeks * weekly_cost"
            }
        }
        
        return resource_estimates
    
    def get_expansion_status_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive status dashboard"""
        current_analysis = self.analyze_current_dataset()
        expansion_plan = self.create_expansion_plan()
        weekly_targets = self.generate_weekly_targets(expansion_plan)
        resource_estimates = self.estimate_resources_required(expansion_plan)
        
        dashboard = {
            "overall_progress": {
                "current_documents": self.current_documents,
                "target_documents": self.target_documents,
                "completion_percentage": (self.current_documents / self.target_documents) * 100,
                "remaining_documents": self.remaining_documents
            },
            "current_analysis": current_analysis,
            "expansion_plan": expansion_plan,
            "weekly_targets": weekly_targets,
            "resource_requirements": resource_estimates,
            "next_actions": [
                "Begin Phase 1: Critical document processing",
                "Set up automated quality validation",
                "Establish weekly progress tracking",
                "Prepare document extraction tools"
            ],
            "risk_factors": [
                "Document availability and accessibility",
                "Quality consistency across different sources",
                "Processing time variations",
                "Storage and bandwidth limitations"
            ],
            "success_indicators": [
                f"Weekly target achievement: {expansion_plan['weekly_target']} docs/week",
                "Quality score maintenance: >= 85%",
                "Processing time efficiency: <= 21 min/document",
                "Zero critical category gaps"
            ]
        }
        
        return dashboard

def main():
    """Main function to demonstrate data expansion strategy"""
    print("📈 Data Expansion Strategy - Week 1 Implementation")
    print("=" * 60)
    
    # Initialize strategy manager
    strategy = DataExpansionStrategy()
    
    # Generate comprehensive dashboard
    print("\n📊 Generating expansion strategy dashboard...")
    dashboard = strategy.get_expansion_status_dashboard()
    
    # Display overall progress
    progress = dashboard["overall_progress"]
    print(f"\n🎯 Overall Progress:")
    print(f"   Current: {progress['current_documents']} documents")
    print(f"   Target: {progress['target_documents']} documents")
    print(f"   Completion: {progress['completion_percentage']:.1f}%")
    print(f"   Remaining: {progress['remaining_documents']} documents")
    
    # Display current gaps
    gaps = dashboard["current_analysis"]["coverage_gaps"]
    if gaps:
        print(f"\n⚠️ Coverage Gaps (Top 5):")
        for gap in gaps[:5]:
            print(f"   {gap['category']}: {gap['current_files']}/{gap['required_files']} "
                  f"({gap['priority']}, urgency: {gap['urgency_score']:.2f})")
    
    # Display expansion plan phases
    phases = dashboard["expansion_plan"]["phases"]
    print(f"\n📋 Expansion Plan Phases:")
    for phase in phases:
        print(f"   Phase {phase['phase']} (Weeks {phase['weeks']}): "
              f"{phase['documents']} docs - {phase['focus']}")
    
    # Display weekly targets
    weekly_targets = dashboard["weekly_targets"]
    print(f"\n📅 Weekly Targets (First 4 weeks):")
    for week_plan in weekly_targets[:4]:
        print(f"   Week {week_plan['week']}: {week_plan['documents_target']} docs "
              f"(Cumulative: {week_plan['cumulative_target']}, "
              f"{week_plan['completion_percentage']:.1f}%)")
    
    # Display resource requirements
    resources = dashboard["resource_requirements"]
    time_req = resources["time_requirements"]
    print(f"\n⏱️ Resource Requirements:")
    print(f"   Total time: {time_req['total_hours']:.0f} hours")
    print(f"   Weekly time: {time_req['weekly_hours']:.0f} hours")
    print(f"   Daily time: {time_req['daily_hours']:.1f} hours")
    
    # Display next actions
    print(f"\n🎯 Next Actions:")
    for action in dashboard["next_actions"]:
        print(f"   • {action}")
    
    # Display success indicators
    print(f"\n✅ Success Indicators:")
    for indicator in dashboard["success_indicators"]:
        print(f"   • {indicator}")
    
    print(f"\n🎉 Data Expansion Strategy Complete!")
    print(f"📊 Ready for systematic document expansion implementation")
    print(f"🎯 Target: {strategy.remaining_documents} documents over 8 weeks")

if __name__ == "__main__":
    main()