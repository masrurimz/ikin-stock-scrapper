#!/usr/bin/env python3
"""
Release script for PSE Scraper
This script helps create releases with executables for multiple platforms
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_git_status():
    """Check if git repository is clean."""
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if result.stdout.strip():
        print("⚠️  Warning: You have uncommitted changes:")
        print(result.stdout)
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    return True


def update_version(version):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return False
    
    content = pyproject_path.read_text()
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if line.startswith('version = '):
            lines[i] = f'version = "{version}"'
            break
    
    pyproject_path.write_text('\n'.join(lines))
    print(f"✅ Updated version to {version} in pyproject.toml")
    return True


def main():
    """Main release function."""
    parser = argparse.ArgumentParser(description="Create a new release")
    parser.add_argument("version", help="Version number (e.g., 2.1.0)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-build", action="store_true", help="Skip building executable")
    parser.add_argument("--push", action="store_true", help="Push changes and tag to remote")
    args = parser.parse_args()
    
    version = args.version
    if not version.startswith('v'):
        version = f"v{version}"
    
    print(f"🚀 Creating release {version}")
    
    # Check git status
    if not check_git_status():
        sys.exit(1)
    
    # Update version
    version_number = version[1:] if version.startswith('v') else version
    if not update_version(version_number):
        sys.exit(1)
    
    # Run tests
    if not args.skip_tests:
        if not run_command("poetry run pytest", "Running tests"):
            print("❌ Tests failed. Fix tests before releasing.")
            sys.exit(1)
    
    # Build executable for current platform
    if not args.skip_build:
        if not run_command("poetry run python build_executable.py --clean", "Building executable"):
            print("❌ Build failed. Fix build issues before releasing.")
            sys.exit(1)
    
    # Commit version change
    if not run_command("git add pyproject.toml", "Staging version change"):
        sys.exit(1)
    
    if not run_command(f'git commit -m "Bump version to {version}"', "Committing version change"):
        sys.exit(1)
    
    # Create git tag
    if not run_command(f'git tag -a {version} -m "Release {version}"', f"Creating tag {version}"):
        sys.exit(1)
    
    # Push if requested
    if args.push:
        if not run_command("git push", "Pushing commits"):
            sys.exit(1)
        
        if not run_command(f"git push origin {version}", f"Pushing tag {version}"):
            sys.exit(1)
        
        print(f"🎉 Release {version} has been pushed to remote!")
        print("📋 Next steps:")
        print("  1. GitHub Actions will automatically build executables for all platforms")
        print("  2. Check the Actions tab for build progress")
        print("  3. Once builds complete, the release will be available in the Releases section")
    else:
        print(f"🎉 Release {version} created locally!")
        print("📋 Next steps:")
        print(f"  1. Push the changes: git push && git push origin {version}")
        print("  2. GitHub Actions will automatically build executables for all platforms")
        print("  3. Check the Actions tab for build progress")


if __name__ == "__main__":
    main()
