#!/usr/bin/env python3
"""
Test runner script for the PSE scraper project.
Provides convenient commands for running different types of tests.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def main():
    parser = argparse.ArgumentParser(description="PSE Scraper Test Runner")
    parser.add_argument(
        "test_type",
        choices=["all", "unit", "integration", "quick", "coverage", "lint"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--file", "-f",
        help="Run tests from specific file"
    )
    
    args = parser.parse_args()
    
    # Change to project directory
    project_root = Path(__file__).parent
    subprocess.run(["cd", str(project_root)], shell=True)
    
    success = True
    
    if args.test_type == "all":
        # Run all tests
        cmd = ["python", "-m", "pytest", "tests/"]
        if args.verbose:
            cmd.append("-v")
        success = run_command(cmd, "All Tests")
        
    elif args.test_type == "unit":
        # Run unit tests only
        cmd = ["python", "-m", "pytest", "tests/", "-m", "unit or not integration"]
        if args.verbose:
            cmd.append("-v")
        success = run_command(cmd, "Unit Tests")
        
    elif args.test_type == "integration":
        # Run integration tests only
        cmd = ["python", "-m", "pytest", "tests/test_integration.py"]
        if args.verbose:
            cmd.append("-v")
        success = run_command(cmd, "Integration Tests")
        
    elif args.test_type == "quick":
        # Run quick tests (excluding slow ones)
        cmd = ["python", "-m", "pytest", "tests/", "-m", "not slow"]
        if args.verbose:
            cmd.append("-v")
        success = run_command(cmd, "Quick Tests")
        
    elif args.test_type == "coverage":
        # Run tests with coverage
        cmd = [
            "python", "-m", "pytest", 
            "tests/",
            "--cov=src/pse_scraper",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=70"
        ]
        success = run_command(cmd, "Tests with Coverage")
        
        if success:
            print("\n📊 Coverage report generated in htmlcov/index.html")
        
    elif args.test_type == "lint":
        # Run code quality checks
        commands = [
            (["python", "-m", "flake8", "src/", "tests/"], "Flake8 Linting"),
            (["python", "-m", "black", "--check", "src/", "tests/"], "Black Code Formatting"),
            (["python", "-m", "isort", "--check-only", "src/", "tests/"], "Import Sorting"),
        ]
        
        for cmd, desc in commands:
            if not run_command(cmd, desc):
                success = False
    
    # Handle specific file testing
    if args.file:
        cmd = ["python", "-m", "pytest", args.file]
        if args.verbose:
            cmd.append("-v")
        success = run_command(cmd, f"Tests in {args.file}")
    
    # Final status
    print(f"\n{'='*60}")
    if success:
        print("🎉 All requested tests completed successfully!")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
