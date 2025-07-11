#!/usr/bin/env python3
"""
Setup script for the YouTube Transcript Viewer application
Sets up virtual environment and installs dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def setup_backend():
    """Set up the backend environment"""
    backend_dir = Path(__file__).parent / "backend"
    print("🔧 Setting up backend...")
    
    # Create virtual environment
    venv_path = backend_dir / "venv"
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=backend_dir, check=True)
    else:
        print("✅ Virtual environment already exists")
    
    # Determine the pip executable path
    if sys.platform == "win32":
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        pip_exe = venv_path / "bin" / "pip"
    
    # Install requirements
    print("📦 Installing Python dependencies...")
    subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], cwd=backend_dir, check=True)
    
    print("✅ Backend setup complete")

def main():
    print("🎬 YouTube Transcript Viewer - Setup Script")
    print("=" * 50)
    
    try:
        # Setup backend
        setup_backend()
        
        print("\n" + "=" * 50)
        print("✅ Setup completed successfully!")
        print("\n📖 Next steps:")
        print("   1. Run: python start.py")
        print("   2. Open: http://localhost:3001")
        print("\n📚 Or start servers individually:")
        print("   Backend:  cd backend && venv/Scripts/python server.py")
        print("   Frontend: cd frontend && python dev_server.py")
        print("=" * 50)
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
