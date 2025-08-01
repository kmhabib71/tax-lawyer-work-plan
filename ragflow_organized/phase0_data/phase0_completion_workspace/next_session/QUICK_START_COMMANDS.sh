#!/bin/bash
# QUICK START COMMANDS FOR NEXT SESSION
# Phase 0 Completion Workspace

echo "=== PHASE 0 COMPLETION WORKSPACE ==="
echo "Current Status: 38% complete (verified)"
echo "Remaining Work: 62% (3-4 weeks)"
echo "Accountability: Truth checker mandatory"
echo ""

# Navigate to workspace
cd /mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ragflow_organized/phase0_data/phase0_completion_workspace

echo "=== STEP 1: VERIFY TRUTH CHECKER WORKS ==="
echo "Running truth validation on last progress report..."
python3 validation/truth_checker.py --validate-report current_progress/CLEAN_DAILY_PROGRESS_REPORT.md
echo ""

echo "=== STEP 2: CHECK CURRENT ASSETS ==="
echo "Legal content file:"
ls -lh extracted_content/extracted_legal_content.json
echo ""
echo "Section count:"
grep -c '"section_number"' extracted_content/extracted_legal_content.json
echo ""
echo "File content preview:"
head -10 extracted_content/extracted_legal_content.json
echo ""

echo "=== STEP 3: TOOLS AVAILABLE ==="
echo "Available tools:"
ls -la tools/
echo ""
echo "Validation system:"
ls -la validation/
echo ""

echo "=== READY TO START WEEK 1 WORK ==="
echo "Priority: Improve legal content quality (15% → 40%)"
echo "First task: Enhance simple_legal_extractor.py"
echo "Target: Extract full content for 100+ sections"
echo ""

echo "=== ACCOUNTABILITY REMINDER ==="
echo "MANDATORY: Run truth checker before any progress claims"
echo "Command: python3 validation/truth_checker.py --validate-report [report].md"
echo "Target: <10% lie detection rate"
echo ""

echo "Workspace ready for Phase 0 completion!"
echo "Current directory: $(pwd)"