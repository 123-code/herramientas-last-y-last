"""
SAST Scanner using Bandit
Runs static analysis on Python code and generates reports
"""

import subprocess
import os
import json
from datetime import datetime

def run_bandit_scan():
    """Execute Bandit SAST scan and generate reports"""
    
    print("=" * 60)
    print("🔍 SAST SCAN - Bandit Security Analysis")
    print("=" * 60)
    
    # Create reports directory
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Define output files
    json_report = os.path.join(reports_dir, 'bandit_report.json')
    html_report = os.path.join(reports_dir, 'bandit_report.html')
    txt_report = os.path.join(reports_dir, 'bandit_report.txt')
    
    # Target file to scan
    target = os.path.join(os.path.dirname(__file__), 'server_main.py')
    
    print(f"\n📁 Scanning: {target}")
    print(f"📊 Reports will be saved to: {reports_dir}")
    
    # Run Bandit with JSON output
    print("\n🔄 Running Bandit analysis...")
    
    try:
        # Generate JSON report
        result = subprocess.run(
            ['bandit', '-r', target, '-f', 'json', '-o', json_report],
            capture_output=True,
            text=True
        )
        
        # Generate HTML report
        subprocess.run(
            ['bandit', '-r', target, '-f', 'html', '-o', html_report],
            capture_output=True,
            text=True
        )
        
        # Generate console output and save to txt
        console_result = subprocess.run(
            ['bandit', '-r', target, '-f', 'txt'],
            capture_output=True,
            text=True
        )
        
        with open(txt_report, 'w') as f:
            f.write(console_result.stdout)
        
        # Parse and display results
        if os.path.exists(json_report):
            with open(json_report, 'r') as f:
                data = json.load(f)
            
            metrics = data.get('metrics', {}).get('_totals', {})
            results = data.get('results', [])
            
            print("\n" + "=" * 60)
            print("📊 SCAN RESULTS SUMMARY")
            print("=" * 60)
            
            print(f"\n📈 Metrics:")
            print(f"   • Lines of Code: {metrics.get('loc', 'N/A')}")
            print(f"   • Lines Skipped: {metrics.get('nosec', 0)}")
            
            # Count by severity
            severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for issue in results:
                severity = issue.get('issue_severity', 'LOW')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            print(f"\n🚨 Vulnerabilities Found: {len(results)}")
            print(f"   • HIGH Severity:   {severity_counts['HIGH']}")
            print(f"   • MEDIUM Severity: {severity_counts['MEDIUM']}")
            print(f"   • LOW Severity:    {severity_counts['LOW']}")
            
            if results:
                print("\n" + "=" * 60)
                print("🔴 DETAILED FINDINGS")
                print("=" * 60)
                
                for i, issue in enumerate(results, 1):
                    severity = issue.get('issue_severity', 'UNKNOWN')
                    confidence = issue.get('issue_confidence', 'UNKNOWN')
                    
                    # Emoji based on severity
                    emoji = "🔴" if severity == "HIGH" else "🟠" if severity == "MEDIUM" else "🟡"
                    
                    print(f"\n{emoji} Issue #{i}: {issue.get('test_id', 'N/A')}")
                    print(f"   Severity: {severity} | Confidence: {confidence}")
                    print(f"   File: {issue.get('filename', 'N/A')}")
                    print(f"   Line: {issue.get('line_number', 'N/A')}")
                    print(f"   Issue: {issue.get('issue_text', 'N/A')}")
                    print(f"   More Info: {issue.get('more_info', 'N/A')}")
            
            print("\n" + "=" * 60)
            print("📁 REPORTS GENERATED")
            print("=" * 60)
            print(f"   • JSON: {json_report}")
            print(f"   • HTML: {html_report}")
            print(f"   • TXT:  {txt_report}")
            print("=" * 60)
            
            return {
                'success': True,
                'total_issues': len(results),
                'high': severity_counts['HIGH'],
                'medium': severity_counts['MEDIUM'],
                'low': severity_counts['LOW'],
                'reports': {
                    'json': json_report,
                    'html': html_report,
                    'txt': txt_report
                }
            }
        else:
            print("❌ Error: JSON report not generated")
            return {'success': False, 'error': 'Report not generated'}
            
    except FileNotFoundError:
        print("❌ Error: Bandit not found. Install with: pip install bandit")
        return {'success': False, 'error': 'Bandit not installed'}
    except Exception as e:
        print(f"❌ Error during scan: {str(e)}")
        return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    result = run_bandit_scan()
    
    if result['success']:
        print(f"\n✅ SAST scan completed successfully!")
        print(f"   Found {result['total_issues']} potential security issues.")
    else:
        print(f"\n❌ SAST scan failed: {result.get('error', 'Unknown error')}")
