#!/usr/bin/env python3
"""
Startup script for the YouTube Transcript Viewer application
Starts the backend server and opens the frontend in browser
"""

import subprocess
import sys
import time
import os
import webbrowser
from pathlib import Path

def start_backend():
    """Start the backend server"""
    backend_dir = Path(__file__).parent / "backend"
    print("🚀 Starting backend server...")
    
    # Check if virtual environment exists
    venv_path = backend_dir / "venv"
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run setup first.")
        return None
    
    # Determine the python executable path
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    
    # Start backend server
    backend_process = subprocess.Popen(
        [str(python_exe), "server.py"],
        cwd=backend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    
    print("✅ Backend server started (PID: {})".format(backend_process.pid))
    return backend_process

def open_frontend():
    """Open the frontend in the default browser"""
    frontend_dir = Path(__file__).parent / "frontend"
    index_path = frontend_dir / "index.html"
    
    if index_path.exists():
        print("🌐 Opening frontend in browser...")
        webbrowser.open(f"file:///{index_path.as_posix()}")
        print("✅ Frontend opened in browser")
    else:
        print("❌ Frontend index.html not found")

def main():
    print("🎬 YouTube Transcript Viewer - Startup Script")
    print("=" * 50)
    
    try:
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            return
        
        # Give backend time to start
        print("⏳ Waiting for backend to start...")
        time.sleep(3)
        
        # Open frontend in browser
        open_frontend()
        
        print("\n" + "=" * 50)
        print("✅ Application is ready!")
        print("🔗 Backend API: http://localhost:3002")
        print("🌐 Frontend: Opened in your default browser")
        print("📝 Or manually open: frontend/index.html")
        print("🛑 Press Ctrl+C to stop the backend server")
        print("=" * 50)
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping backend server...")
            backend_process.terminate()
            print("✅ Backend server stopped")
    
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
