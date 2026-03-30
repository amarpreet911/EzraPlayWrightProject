#!/usr/bin/env python
"""
Complete Test Runner - Runs all tests in the tests/ folder
Supports multiple execution modes and options
"""

import subprocess
import sys
import os
from pathlib import Path

# Resolve project root relative to this script — works on any machine/OS
PROJECT_ROOT = str(Path(__file__).resolve().parent)

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70 + "\n")

def run_all_tests_verbose():
    """Run all tests with verbose output and live printing"""
    print_header("Running ALL Tests (Verbose Mode)")
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         'tests/',
         '-v', '-s',
         '--tb=short',
         '--timeout=300'],
        cwd=PROJECT_ROOT
    )
    
    return result.returncode

def run_all_tests_quiet():
    """Run all tests with minimal output"""
    print_header("Running ALL Tests (Quiet Mode)")
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         'tests/',
         '-v',
         '--tb=short',
         '--timeout=300'],
        cwd=PROJECT_ROOT
    )
    
    return result.returncode

def run_all_tests_with_report():
    """Run all tests and generate HTML report"""
    print_header("Running ALL Tests (With HTML Report)")
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         'tests/',
         '-v', '-s',
         '--tb=short',
         '--timeout=300',
         '--html=test_report.html',
         '--self-contained-html'],
        cwd=PROJECT_ROOT
    )
    
    if result.returncode == 0:
        print("\n✅ Test report generated: test_report.html")
    
    return result.returncode

def run_tests_by_marker(marker):
    """Run tests by marker (e.g., 'signup', 'booking')"""
    print_header(f"Running Tests Marked '{marker}'")
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         'tests/',
         '-m', marker,
         '-v', '-s',
         '--tb=short',
         '--timeout=300'],
        cwd=PROJECT_ROOT
    )
    
    return result.returncode

def run_tests_by_directory(test_dir):
    """Run tests in a specific directory"""
    print_header(f"Running Tests in {test_dir}")
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         test_dir,
         '-v', '-s',
         '--tb=short',
         '--timeout=300'],
        cwd=PROJECT_ROOT
    )
    
    return result.returncode

def show_available_tests():
    """List all available tests"""
    print_header("Available Tests")
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         'tests/',
         '--collect-only', '-q'],
        cwd=PROJECT_ROOT
    )
    
    return result.returncode

def show_help():
    """Show help information"""
    print_header("Test Runner Help")
    print("""
USAGE: python run_all_tests.py [OPTION]

OPTIONS:
  (no option)           Run all tests in verbose mode (default)
  --quiet               Run all tests with minimal output
  --report              Run all tests and generate HTML report
  --collect             List all available tests
  --marker <name>       Run tests with specific marker (signup, booking, etc)
  --dir <path>          Run tests in specific directory
  --help                Show this help message

EXAMPLES:
  python run_all_tests.py
  python run_all_tests.py --quiet
  python run_all_tests.py --report
  python run_all_tests.py --collect
  python run_all_tests.py --marker signup
  python run_all_tests.py --dir tests/test_booking
  python run_all_tests.py --help

MARKERS AVAILABLE:
  - signup              Tests for signup functionality
  - booking             Tests for booking functionality
  - user_login          Tests for user login functionality
  - select_plan         Tests for plan selection

DEFAULT BEHAVIOR:
  - Verbose output (-v -s flags)
  - Short tracebacks on failure (--tb=short)
  - 5-minute timeout per test (--timeout=300)
  - Real-time printing of test output
    """)

def main():
    """Main entry point"""
    os.chdir(PROJECT_ROOT)
    
    # Check if tests directory exists
    if not Path('tests').is_dir():
        print("❌ ERROR: 'tests' directory not found!")
        return 1
    
    # Parse arguments
    args = sys.argv[1:]
    
    if not args or args[0] == '--verbose':
        exit_code = run_all_tests_verbose()
    elif args[0] == '--quiet':
        exit_code = run_all_tests_quiet()
    elif args[0] == '--report':
        exit_code = run_all_tests_with_report()
    elif args[0] == '--collect':
        exit_code = show_available_tests()
    elif args[0] == '--marker' and len(args) > 1:
        exit_code = run_tests_by_marker(args[1])
    elif args[0] == '--dir' and len(args) > 1:
        exit_code = run_tests_by_directory(args[1])
    elif args[0] == '--help':
        show_help()
        return 0
    else:
        print(f"❌ Unknown option: {args[0]}")
        print("Use --help for available options")
        return 1
    
    # Print summary
    print()
    print("=" * 70)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print(f"Exit Code: {exit_code}")
    print("=" * 70)
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())

