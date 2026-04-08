#!/usr/bin/env python3
"""
Hugging Face Spaces Application Entry Point
This is the main entry point for the OpenEnv GridWorld Space.
"""

import os
import sys
import subprocess
import time
import requests
from threading import Thread

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the inference app
from inference import app

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import requests
        print("✅ All Python dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def start_nodejs_server():
    """Start the Node.js server in a separate process"""
    try:
        print("🚀 Starting Node.js server...")
        
        # Start Node.js server
        process = subprocess.Popen(
            ["node", "index.js"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server started successfully
        try:
            response = requests.get("http://localhost:7860/api/env/info", timeout=10)
            if response.status_code == 200:
                print("✅ Node.js server started successfully")
                return process
            else:
                print(f"❌ Node.js server returned status: {response.status_code}")
                process.terminate()
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to Node.js server: {e}")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Failed to start Node.js server: {e}")
        return None

def main():
    """Main entry point for Hugging Face Spaces"""
    print("🌍 OpenEnv GridWorld - Hugging Face Space")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Please install required dependencies")
        sys.exit(1)
    
    # Start Node.js server
    nodejs_process = start_nodejs_server()
    
    if nodejs_process:
        print("🚀 Starting FastAPI server...")
        print("🌐 OpenEnv GridWorld is ready!")
        print("   Visit the Space URL to interact with the environment")
        
        # Start FastAPI server
        import uvicorn
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=7860,
            reload=False,
            log_level="info"
        )
        
        # Cleanup
        if nodejs_process:
            nodejs_process.terminate()
    else:
        print("❌ Failed to start Node.js server")
        print("Please check that Node.js is installed and index.js is present")
        sys.exit(1)

if __name__ == "__main__":
    main()