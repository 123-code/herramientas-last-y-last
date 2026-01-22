#!/usr/bin/env python3
"""
Test Runner Script for Security Pipeline Demo
Runs unit tests for the security pipeline components
"""

import subprocess
import sys
import os

def run_tests():
    """Run the test suite"""
    print("🔬 Running Security Pipeline Unit Tests")
    print("=" * 50)

    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Install with: pip install -r requirements-test.txt")
        return False

    # Run tests
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            '--tb=short',
            '--verbose',
            'test_security_pipeline.py',
            'test_flask_app.py'
        ], capture_output=False, text=True)

        return result.returncode == 0

    except FileNotFoundError:
        print("❌ pytest not found in PATH")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_coverage():
    """Run tests with coverage report"""
    print("📊 Running Tests with Coverage")
    print("=" * 50)

    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            '--cov=.',
            '--cov-report=html',
            '--cov-report=term-missing',
            'test_security_pipeline.py',
            'test_flask_app.py'
        ], capture_output=False, text=True)

        if result.returncode == 0:
            print("\n📁 HTML coverage report saved to: htmlcov/index.html")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running coverage: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--coverage':
        success = run_coverage()
    else:
        success = run_tests()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
