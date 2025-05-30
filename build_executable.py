#!/usr/bin/env python3
"""
Build script for creating platform-specific executables of PSE Scraper
Supports Windows, macOS, and Linux builds
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
import argparse

# Configure UTF-8 encoding for Windows
if platform.system().lower() == "windows":
    import locale
    # Set environment variables for UTF-8 support
    os.environ["PYTHONIOENCODING"] = "utf-8"
    # Reconfigure stdout/stderr for UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')


def get_platform_info():
    """Get current platform information."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        if machine == "arm64":
            return "macos-arm64"
        else:
            return "macos-x64"
    elif system == "windows":
        if machine in ["amd64", "x86_64"]:
            return "windows-x64"
        else:
            return "windows-x86"
    elif system == "linux":
        if machine in ["amd64", "x86_64"]:
            return "linux-x64"
        elif machine in ["aarch64", "arm64"]:
            return "linux-arm64"
        else:
            return "linux-x86"
    else:
        return f"{system}-{machine}"


def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}/...")
            shutil.rmtree(dir_name)


def install_dependencies():
    """Install build dependencies."""
    print("📦 Installing build dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True


def build_executable(platform_name):
    """Build the executable using PyInstaller."""
    print(f"🔨 Building executable for {platform_name}...")
    
    try:
        # Run PyInstaller with the spec file
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "pse-scraper.spec"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build completed successfully")
            return True
        else:
            print(f"❌ Build failed with return code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def create_release_package(platform_name):
    """Create a release package with the executable."""
    dist_dir = Path("dist")
    release_dir = Path("releases")
    
    # Create releases directory
    release_dir.mkdir(exist_ok=True)
    
    # Determine executable name based on platform
    if platform.system().lower() == "windows":
        exe_name = "pse-scraper.exe"
    else:
        exe_name = "pse-scraper"
    
    exe_path = dist_dir / exe_name
    
    if not exe_path.exists():
        print(f"❌ Executable not found at {exe_path}")
        return False
    
    # Create platform-specific release name
    release_name = f"pse-scraper-{platform_name}"
    if platform.system().lower() == "windows":
        release_name += ".exe"
    
    release_path = release_dir / release_name
    
    # Copy executable to releases directory
    shutil.copy2(exe_path, release_path)
    
    # Make executable on Unix-like systems
    if platform.system().lower() != "windows":
        os.chmod(release_path, 0o755)
    
    print(f"📦 Release package created: {release_path}")
    print(f"📊 File size: {release_path.stat().st_size / (1024*1024):.1f} MB")
    
    return True


def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Build PSE Scraper executable")
    parser.add_argument("--clean", action="store_true", help="Clean build directories before building")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    args = parser.parse_args()
    
    platform_name = get_platform_info()
    print(f"🚀 Building PSE Scraper for {platform_name}")
    
    if args.clean:
        clean_build_dirs()
    
    if not args.skip_deps:
        if not install_dependencies():
            sys.exit(1)
    
    if not build_executable(platform_name):
        sys.exit(1)
    
    if not create_release_package(platform_name):
        sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print(f"📁 Executable available in: releases/pse-scraper-{platform_name}")
    print("\n📋 Next steps:")
    print("  1. Test the executable on your target platform")
    print("  2. Upload to GitHub releases or distribute as needed")
    print("  3. Create builds for other platforms if needed")


if __name__ == "__main__":
    main()
