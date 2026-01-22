"""
DAST Scanner using OWASP ZAP
Runs dynamic analysis on the running web application
"""

import subprocess
import os
import time
import sys

def run_zap_baseline_scan(target_url="http://localhost:5000"):
    """
    Execute OWASP ZAP baseline scan using Docker
    This is a quick scan suitable for CI/CD pipelines
    """
    
    print("=" * 60)
    print("🌐 DAST SCAN - OWASP ZAP Security Analysis")
    print("=" * 60)
    
    # Create reports directory
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Report file paths
    html_report = os.path.join(reports_dir, 'zap_report.html')
    json_report = os.path.join(reports_dir, 'zap_report.json')
    
    print(f"\n🎯 Target URL: {target_url}")
    print(f"📁 Reports directory: {reports_dir}")
    
    # Check if Docker is available
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: Docker is not installed or not running")
        print("   Please install Docker Desktop and try again")
        return {'success': False, 'error': 'Docker not available'}
    
    print("\n🔄 Starting OWASP ZAP baseline scan...")
    print("   This may take a few minutes...\n")
    
    # ZAP Baseline scan command
    # Using host.docker.internal for Windows/Mac to access host's localhost
    docker_target = target_url.replace('localhost', 'host.docker.internal')
    
    cmd = [
        'docker', 'run', '--rm',
        '-v', f'{reports_dir}:/zap/wrk:rw',
        '--add-host=host.docker.internal:host-gateway',
        'ghcr.io/zaproxy/zaproxy:stable',
        'zap-baseline.py',
        '-t', docker_target,
        '-r', 'zap_report.html',
        '-J', 'zap_report.json',
        '-I'  # Continue even if warnings found
    ]
    
    print(f"📌 Running command:")
    print(f"   {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        print("\n" + "=" * 60)
        print("📊 ZAP SCAN OUTPUT")
        print("=" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ Warnings/Errors:")
            print(result.stderr)
        
        # Check if reports were generated
        reports_generated = []
        if os.path.exists(html_report):
            reports_generated.append(f"HTML: {html_report}")
        if os.path.exists(json_report):
            reports_generated.append(f"JSON: {json_report}")
        
        print("\n" + "=" * 60)
        print("📁 REPORTS GENERATED")
        print("=" * 60)
        for report in reports_generated:
            print(f"   • {report}")
        
        # Return code meanings:
        # 0: No warnings
        # 1: Only informational alerts
        # 2: Warnings found (fail as per CI/CD standards)
        # 3: Error during scan
        
        scan_result = {
            'success': True,
            'return_code': result.returncode,
            'reports': {
                'html': html_report if os.path.exists(html_report) else None,
                'json': json_report if os.path.exists(json_report) else None
            }
        }
        
        if result.returncode == 0:
            print("\n✅ No security issues found!")
        elif result.returncode == 1:
            print("\n⚠️ Informational alerts found")
        elif result.returncode == 2:
            print("\n🔴 Security warnings found!")
        else:
            print(f"\n❌ Scan completed with return code: {result.returncode}")
        
        return scan_result
        
    except subprocess.TimeoutExpired:
        print("❌ Error: Scan timed out after 10 minutes")
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        print(f"❌ Error during scan: {str(e)}")
        return {'success': False, 'error': str(e)}


def run_zap_full_scan(target_url="http://localhost:5000"):
    """
    Execute OWASP ZAP full scan (more thorough but slower)
    """
    
    print("=" * 60)
    print("🌐 DAST FULL SCAN - OWASP ZAP")
    print("=" * 60)
    
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    docker_target = target_url.replace('localhost', 'host.docker.internal')
    
    cmd = [
        'docker', 'run', '--rm',
        '-v', f'{reports_dir}:/zap/wrk:rw',
        '--add-host=host.docker.internal:host-gateway',
        'ghcr.io/zaproxy/zaproxy:stable',
        'zap-full-scan.py',
        '-t', docker_target,
        '-r', 'zap_full_report.html',
        '-J', 'zap_full_report.json',
        '-I'
    ]
    
    print(f"\n🎯 Target: {target_url}")
    print("⏱️ Full scan may take 15-30 minutes...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        print(result.stdout)
        return {'success': True, 'output': result.stdout}
    except Exception as e:
        return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    # Default to baseline scan
    scan_type = sys.argv[1] if len(sys.argv) > 1 else 'baseline'
    target = sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:5000'
    
    if scan_type == 'full':
        result = run_zap_full_scan(target)
    else:
        result = run_zap_baseline_scan(target)
    
    if result['success']:
        print(f"\n✅ DAST scan completed!")
    else:
        print(f"\n❌ DAST scan failed: {result.get('error', 'Unknown error')}")
