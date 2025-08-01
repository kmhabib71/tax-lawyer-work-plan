#!/usr/bin/env python3
"""
Automated truth verification for all project claims
Usage: python3 truth_checker.py --validate-report report.md
"""

import os
import re
import json
import subprocess
from pathlib import Path

class TruthChecker:
    def __init__(self):
        self.lies_detected = []
        self.verified_claims = []
        self.suspicious_patterns = [
            r'100%\s*complete',
            r'50,000\+',
            r'200\+\s*rules',
            r'comprehensive',
            r'complete\s*legal\s*framework',
            r'fully\s*automated'
        ]
        
        # Anti-exaggeration rules
        self.exaggeration_indicators = [
            r'amazing', r'incredible', r'outstanding', r'perfect', r'flawless',
            r'revolutionary', r'breakthrough', r'unprecedented', r'exceptional',
            r'remarkable', r'extraordinary', r'fantastic', r'awesome',
            r'successfully\s+achieved', r'major\s+breakthrough', r'significant\s+achievement'
        ]
        
    def validate_report(self, report_path):
        """Validate all claims in a progress report"""
        if not os.path.exists(report_path):
            return f"❌ Report file does not exist: {report_path}"
            
        with open(report_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract all claims
        claims = self.extract_claims(content)
        
        # Validate each claim
        validation_results = []
        for claim in claims:
            result = self.verify_claim(claim)
            validation_results.append({
                'claim': claim,
                'result': result
            })
            
            if result['status'] == 'FAIL':
                self.lies_detected.append({'claim': claim, 'reason': result['reason']})
            else:
                self.verified_claims.append(claim)
        
        return self.generate_truth_report(validation_results)
    
    def extract_claims(self, content):
        """Extract verifiable claims from report"""
        claims = []
        
        # Look for percentage claims
        percentage_matches = re.findall(r'(\d+)%[^0-9]*?(complete|done|finished|achieved)', content, re.IGNORECASE)
        for match in percentage_matches:
            claims.append({
                'type': 'percentage',
                'value': int(match[0]),
                'context': match[1],
                'original_text': f"{match[0]}% {match[1]}"
            })
        
        # Look for file claims with paths
        file_matches = re.findall(r'`([^`]+\.(?:json|py|md|txt))`', content)
        for file_path in file_matches:
            claims.append({
                'type': 'file_exists',
                'path': file_path,
                'original_text': f"`{file_path}`"
            })
        
        # Look for numerical claims (rules, provisions, etc.)
        number_matches = re.findall(r'(\d+(?:,\d+)*)\+?\s*(rules|provisions|sections|files|terms|lines)', content, re.IGNORECASE)
        for match in number_matches:
            claims.append({
                'type': 'numerical',
                'count': int(match[0].replace(',', '')),
                'item_type': match[1],
                'original_text': f"{match[0]}+ {match[1]}"
            })
        
        # Look for suspicious superlative claims
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                claims.append({
                    'type': 'suspicious',
                    'pattern': pattern,
                    'text': match,
                    'original_text': match
                })
        
        # Look for exaggeration indicators
        for pattern in self.exaggeration_indicators:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                claims.append({
                    'type': 'exaggeration',
                    'pattern': pattern,
                    'text': match,
                    'original_text': match
                })
        
        return claims
    
    def verify_claim(self, claim):
        """Verify a specific claim"""
        if claim['type'] == 'file_exists':
            return self.verify_file_exists(claim['path'])
        elif claim['type'] == 'percentage':
            return self.verify_percentage_claim(claim)
        elif claim['type'] == 'numerical':
            return self.verify_numerical_claim(claim)
        elif claim['type'] == 'suspicious':
            return self.verify_suspicious_claim(claim)
        elif claim['type'] == 'exaggeration':
            return self.verify_exaggeration_claim(claim)
        
        return {'status': 'UNKNOWN', 'reason': 'Unknown claim type'}
    
    def verify_file_exists(self, file_path):
        """Verify file actually exists and has substantial content"""
        base_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap"
        
        # Try different possible paths
        possible_paths = [
            file_path,
            os.path.join(base_dir, file_path),
            os.path.join(base_dir, "precise_structured_laws", file_path),
            os.path.join(base_dir, "ragflow", "data", file_path),
            os.path.join(base_dir, "structured_tax_data", file_path)
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                # Check file size
                size = os.path.getsize(path)
                if size < 500:  # Less than 500 bytes is suspicious for claimed substantial files
                    return {
                        'status': 'FAIL', 
                        'reason': f'File too small: {size} bytes (likely empty/placeholder)',
                        'evidence': f'File exists but size: {size} bytes'
                    }
                
                # Check for placeholder content
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        first_1000_chars = f.read(1000)
                        placeholder_indicators = [
                            'placeholder', 'todo', 'fixme', 'empty', 'phase_0_placeholder',
                            'needs verification', 'to be implemented', 'coming soon'
                        ]
                        
                        found_placeholders = [p for p in placeholder_indicators if p in first_1000_chars.lower()]
                        if found_placeholders:
                            return {
                                'status': 'FAIL',
                                'reason': f'Contains placeholder content: {found_placeholders}',
                                'evidence': f'Placeholder indicators found: {found_placeholders}'
                            }
                        
                        # Check if file is mostly empty structure (like JSON with empty arrays)
                        if file_path.endswith('.json'):
                            try:
                                data = json.loads(first_1000_chars)
                                if isinstance(data, dict):
                                    # Count non-empty values
                                    non_empty_count = sum(1 for v in data.values() if v)
                                    if non_empty_count == 0:
                                        return {
                                            'status': 'FAIL',
                                            'reason': 'JSON file contains only empty structures',
                                            'evidence': 'All JSON values are empty'
                                        }
                            except json.JSONDecodeError:
                                pass  # Not valid JSON, but that's okay for content check
                
                except Exception as e:
                    return {
                        'status': 'FAIL',
                        'reason': f'Cannot read file: {e}',
                        'evidence': f'File exists but unreadable: {path}'
                    }
                
                return {
                    'status': 'PASS', 
                    'evidence': f'File exists: {path}, Size: {size} bytes, Contains actual content'
                }
        
        return {
            'status': 'FAIL', 
            'reason': 'File does not exist in any expected location',
            'evidence': f'Searched paths: {possible_paths}'
        }
    
    def verify_percentage_claim(self, claim):
        """Verify percentage completion claims"""
        if claim['value'] == 100:
            return {
                'status': 'FAIL',
                'reason': 'Suspicious 100% completion claim - requires extraordinary evidence',
                'evidence': 'Perfect completion percentages are statistically unlikely'
            }
        elif claim['value'] > 95:
            return {
                'status': 'WARNING',
                'reason': f'{claim["value"]}% completion is very high - needs strong evidence',
                'evidence': 'High completion percentages require detailed verification'
            }
        else:
            return {
                'status': 'PASS',
                'evidence': f'{claim["value"]}% is reasonable completion percentage'
            }
    
    def verify_numerical_claim(self, claim):
        """Verify numerical claims like '50,000+ provisions'"""
        suspicious_numbers = {
            'provisions': {'threshold': 10000, 'typical_max': 5000},
            'rules': {'threshold': 500, 'typical_max': 100},
            'sections': {'threshold': 200, 'typical_max': 100},
            'terms': {'threshold': 1000, 'typical_max': 500}
        }
        
        item_type = claim['item_type'].lower()
        if item_type in suspicious_numbers:
            threshold = suspicious_numbers[item_type]['threshold']
            if claim['count'] > threshold:
                return {
                    'status': 'FAIL',
                    'reason': f'{claim["count"]} {item_type} is unrealistically high (threshold: {threshold})',
                    'evidence': f'Typical maximum for {item_type}: {suspicious_numbers[item_type]["typical_max"]}'
                }
        
        return {
            'status': 'PASS',
            'evidence': f'{claim["count"]} {item_type} is within reasonable range'
        }
    
    def verify_suspicious_claim(self, claim):
        """Verify suspicious superlative claims"""
        return {
            'status': 'WARNING',
            'reason': f'Suspicious superlative claim detected: "{claim["text"]}"',
            'evidence': 'Claims using absolute terms like "complete", "comprehensive" need strong evidence'
        }
    
    def verify_exaggeration_claim(self, claim):
        """Verify exaggeration claims"""
        return {
            'status': 'FAIL',
            'reason': f'Exaggeration detected: "{claim["text"]}" - Use factual, non-promotional language',
            'evidence': 'Technical reports should use neutral, factual language instead of promotional terms'
        }
    
    def generate_truth_report(self, validation_results):
        """Generate comprehensive truth verification report"""
        total_claims = len(validation_results)
        failed_claims = len([r for r in validation_results if r['result']['status'] == 'FAIL'])
        warning_claims = len([r for r in validation_results if r['result']['status'] == 'WARNING'])
        passed_claims = len([r for r in validation_results if r['result']['status'] == 'PASS'])
        
        lie_percentage = (failed_claims / total_claims * 100) if total_claims > 0 else 0
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    TRUTH VERIFICATION REPORT                 ║
╚══════════════════════════════════════════════════════════════╝

📊 CLAIM ANALYSIS SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Claims Analyzed: {total_claims}
✅ Verified Claims: {passed_claims}
⚠️  Warning Claims: {warning_claims}
❌ False Claims: {failed_claims}
📈 Lie Detection Rate: {lie_percentage:.1f}%

🎯 CREDIBILITY ASSESSMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if lie_percentage == 0 and warning_claims == 0:
            report += "✅ FULLY CREDIBLE - All claims verified without issues\n"
        elif lie_percentage == 0 and warning_claims > 0:
            report += "⚠️  MOSTLY CREDIBLE - No false claims but some warnings\n"
        elif lie_percentage < 20:
            report += "🚨 QUESTIONABLE CREDIBILITY - Some false claims detected\n"
        elif lie_percentage < 50:
            report += "❌ LOW CREDIBILITY - Many false claims detected\n"
        else:
            report += "💀 NOT CREDIBLE - Majority of claims are false\n"
        
        # Detailed results
        if failed_claims > 0:
            report += "\n❌ FALSE CLAIMS DETECTED:\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            fail_count = 1
            for result in validation_results:
                if result['result']['status'] == 'FAIL':
                    claim = result['claim']
                    reason = result['result']['reason']
                    evidence = result['result'].get('evidence', 'No evidence provided')
                    
                    report += f"{fail_count}. CLAIM: \"{claim['original_text']}\"\n"
                    report += f"   REASON: {reason}\n"
                    report += f"   EVIDENCE: {evidence}\n\n"
                    fail_count += 1
        
        if warning_claims > 0:
            report += "\n⚠️  WARNING CLAIMS:\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            warn_count = 1
            for result in validation_results:
                if result['result']['status'] == 'WARNING':
                    claim = result['claim']
                    reason = result['result']['reason']
                    
                    report += f"{warn_count}. CLAIM: \"{claim['original_text']}\"\n"
                    report += f"   WARNING: {reason}\n\n"
                    warn_count += 1
        
        if passed_claims > 0:
            report += f"\n✅ VERIFIED CLAIMS ({passed_claims}):\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            pass_count = 1
            for result in validation_results:
                if result['result']['status'] == 'PASS':
                    claim = result['claim']
                    report += f"{pass_count}. \"{claim['original_text']}\" ✅\n"
                    pass_count += 1
        
        report += "\n" + "="*60 + "\n"
        report += "RECOMMENDATION:\n"
        
        if lie_percentage > 20:
            report += "🚨 HIGH LIE RATE DETECTED - All claims should be re-verified with evidence\n"
            report += "📋 REQUIRED ACTIONS:\n"
            report += "   1. Provide evidence for all failed claims\n"
            report += "   2. Remove or correct false statements\n"
            report += "   3. Add disclaimers for uncertain claims\n"
            report += "   4. Re-run truth verification after corrections\n"
        elif warning_claims > 5:
            report += "⚠️  Many warning claims - provide additional evidence for suspicious claims\n"
        else:
            report += "✅ Acceptable credibility level - minor corrections may be needed\n"
        
        return report

def main():
    import sys
    
    if len(sys.argv) != 3 or sys.argv[1] != "--validate-report":
        print("Usage: python3 truth_checker.py --validate-report report.md")
        print("Example: python3 truth_checker.py --validate-report PHASE_0_ACHIEVEMENT_REPORT.md")
        sys.exit(1)
    
    report_path = sys.argv[2]
    checker = TruthChecker()
    result = checker.validate_report(report_path)
    print(result)
    
    # Exit with error code if lies detected
    if len(checker.lies_detected) > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()