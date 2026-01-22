"""
Security Pipeline Orchestrator
Runs both SAST (Bandit) and DAST (OWASP ZAP) scans sequentially
"""

import subprocess
import os
import sys
import time
import json
from datetime import datetime
import threading
import signal

# Add the current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from run_sast import run_bandit_scan
from run_dast import run_zap_baseline_scan


def print_banner():
    """Print the security pipeline banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🔒 CORPORATE SECURITY PIPELINE                                  ║
║                                                                   ║
║   SAST: Bandit (Static Analysis)                                  ║
║   DAST: OWASP ZAP (Dynamic Analysis)                              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_flask_app():
    """Start the Flask application in a subprocess"""
    app_path = os.path.join(os.path.dirname(__file__), 'server_main.py')
    return subprocess.Popen(
        [sys.executable, app_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )


def wait_for_app(url="http://localhost:5000", timeout=30):
    """Wait for the Flask app to be ready"""
    import urllib.request
    
    print(f"⏳ Waiting for application at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            urllib.request.urlopen(url, timeout=2)
            print("✅ Application is ready!")
            return True
        except:
            time.sleep(1)
    
    print("❌ Timeout waiting for application")
    return False


def generate_consolidated_report(sast_result, dast_result):
    """Generate a consolidated security report"""
    
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    report_path = os.path.join(reports_dir, 'security_pipeline_report.html')
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # SAST summary
    sast_summary = "❌ Failed" if not sast_result.get('success') else f"""
        <ul>
            <li>High Severity: {sast_result.get('high', 0)}</li>
            <li>Medium Severity: {sast_result.get('medium', 0)}</li>
            <li>Low Severity: {sast_result.get('low', 0)}</li>
            <li>Total Issues: {sast_result.get('total_issues', 0)}</li>
        </ul>
    """
    
    # DAST summary  
    dast_summary = "❌ Failed" if not dast_result.get('success') else """
        <p>✅ Scan completed. See detailed report for findings.</p>
    """
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Security Pipeline Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            margin: 0;
            padding: 40px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        h1 {{
            color: #e94560;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #888;
            margin-bottom: 40px;
        }}
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
        }}
        .card h2 {{
            color: #e94560;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .success {{ color: #4ade80; }}
        .warning {{ color: #fbbf24; }}
        .error {{ color: #f87171; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        th {{
            background: rgba(233, 69, 96, 0.2);
            color: #e94560;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .badge-high {{ background: #dc2626; }}
        .badge-medium {{ background: #f59e0b; }}
        .badge-low {{ background: #3b82f6; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Corporate Security Pipeline Report</h1>
        <p class="subtitle">Generated: {timestamp}</p>
        
        <div class="card">
            <h2>📊 Executive Summary</h2>
            <table>
                <tr>
                    <th>Scan Type</th>
                    <th>Tool</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>SAST (Static Analysis)</td>
                    <td>Bandit</td>
                    <td class="{'success' if sast_result.get('success') else 'error'}">
                        {'✅ Completed' if sast_result.get('success') else '❌ Failed'}
                    </td>
                </tr>
                <tr>
                    <td>DAST (Dynamic Analysis)</td>
                    <td>OWASP ZAP</td>
                    <td class="{'success' if dast_result.get('success') else 'error'}">
                        {'✅ Completed' if dast_result.get('success') else '❌ Failed'}
                    </td>
                </tr>
            </table>
        </div>
        
        <div class="card">
            <h2>🔍 SAST Results (Bandit)</h2>
            {sast_summary}
        </div>
        
        <div class="card">
            <h2>🌐 DAST Results (OWASP ZAP)</h2>
            {dast_summary}
        </div>
        
        <div class="card">
            <h2>📁 Detailed Reports</h2>
            <ul>
                <li><a href="bandit_report.html" style="color: #e94560;">Bandit SAST Report (HTML)</a></li>
                <li><a href="bandit_report.json" style="color: #e94560;">Bandit SAST Report (JSON)</a></li>
                <li><a href="zap_report.html" style="color: #e94560;">OWASP ZAP DAST Report (HTML)</a></li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Security Pipeline Demo - Bandit + OWASP ZAP</p>
        </div>
    </div>
</body>
</html>
    """
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n📄 Consolidated report saved to: {report_path}")
    return report_path


def run_pipeline(run_dast=True):
    """
    Run the complete security pipeline
    
    Args:
        run_dast: If True, also runs DAST scan (requires Docker)
    """
    print_banner()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🕐 Pipeline started at: {timestamp}")
    print(f"📂 Working directory: {os.path.dirname(__file__)}")
    
    results = {
        'sast': None,
        'dast': None
    }
    
    flask_process = None
    
    try:
        # ============================================
        # PHASE 1: SAST Scan with Bandit
        # ============================================
        print("\n" + "=" * 70)
        print("📌 PHASE 1: Static Application Security Testing (SAST)")
        print("=" * 70)
        
        results['sast'] = run_bandit_scan()
        
        if not run_dast:
            print("\n⏭️ Skipping DAST scan (use --full to include DAST)")
        else:
            # ============================================
            # PHASE 2: Start Flask Application
            # ============================================
            print("\n" + "=" * 70)
            print("📌 PHASE 2: Starting Target Application")
            print("=" * 70)
            
            print("\n🚀 Starting Flask application...")
            flask_process = run_flask_app()
            
            if wait_for_app():
                # ============================================
                # PHASE 3: DAST Scan with OWASP ZAP
                # ============================================
                print("\n" + "=" * 70)
                print("📌 PHASE 3: Dynamic Application Security Testing (DAST)")
                print("=" * 70)
                
                results['dast'] = run_zap_baseline_scan()
            else:
                results['dast'] = {'success': False, 'error': 'App not ready'}
        
        # ============================================
        # PHASE 4: Generate Consolidated Report
        # ============================================
        print("\n" + "=" * 70)
        print("📌 PHASE 4: Generating Consolidated Report")
        print("=" * 70)
        
        if results['dast'] is None:
            results['dast'] = {'success': False, 'error': 'Skipped'}
        
        report_path = generate_consolidated_report(results['sast'], results['dast'])
        
        # ============================================
        # Summary
        # ============================================
        print("\n" + "=" * 70)
        print("🏁 PIPELINE COMPLETE")
        print("=" * 70)
        
        print("\n📊 Results Summary:")
        print(f"   • SAST (Bandit): {'✅ Success' if results['sast'].get('success') else '❌ Failed'}")
        if results['sast'].get('success'):
            print(f"     - Found {results['sast'].get('total_issues', 0)} security issues")
        
        print(f"   • DAST (ZAP): {'✅ Success' if results['dast'].get('success') else '❌ ' + results['dast'].get('error', 'Failed')}")
        
        print(f"\n📁 Reports available in: {os.path.join(os.path.dirname(__file__), 'reports')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline interrupted by user")
    finally:
        # Clean up Flask process
        if flask_process:
            print("\n🛑 Stopping Flask application...")
            if os.name == 'nt':
                flask_process.terminate()
            else:
                os.kill(flask_process.pid, signal.SIGTERM)
            flask_process.wait()
            print("✅ Flask application stopped")
    
    return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Security Pipeline Demo')
    parser.add_argument('--sast-only', action='store_true', 
                        help='Run only SAST scan (no Docker required)')
    parser.add_argument('--full', action='store_true',
                        help='Run full pipeline including DAST (requires Docker)')
    
    args = parser.parse_args()
    
    # By default, run SAST only for easier demo
    run_dast = args.full and not args.sast_only
    
    if not args.full and not args.sast_only:
        print("💡 Tip: Use --full to include DAST scan (requires Docker)")
        print("       Use --sast-only to run only Bandit analysis")
        print("")
    
    run_pipeline(run_dast=run_dast)


if __name__ == '__main__':
    main()
