#!/usr/bin/env python3
"""
OpenEnv GridWorld - Hugging Face Inference Script
Simple inference script for Hugging Face Spaces compatibility.
"""

import os
import subprocess
import time
import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Create FastAPI app
app = FastAPI(
    title="OpenEnv GridWorld",
    description="Reinforcement Learning Environment for Hugging Face Spaces"
)

# Serve static files
app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serve the main HTML interface"""
    try:
        with open("public/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>OpenEnv GridWorld</h1><p>Files not found. Please check deployment.</p>"

@app.get("/about", response_class=HTMLResponse)
async def read_about():
    """Serve about page"""
    try:
        with open("public/about.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>About</h1><p>Files not found.</p>"

@app.get("/home", response_class=HTMLResponse)
async def read_home():
    """Serve home page"""
    try:
        with open("public/home.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Home</h1><p>Files not found.</p>"

# Proxy functions to Node.js server
def proxy_request(path, method="GET", data=None):
    """Proxy requests to Node.js server"""
    try:
        url = f"http://localhost:7860{path}"
        if method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return {"error": "Invalid method"}
        
        return response.json()
    except Exception as e:
        return {"error": str(e), "message": "Node.js server may not be running"}

@app.post("/api/reset")
async def api_reset(request: Request):
    """Reset environment"""
    data = await request.json()
    return proxy_request("/api/reset", "POST", data)

@app.post("/api/step")
async def api_step(request: Request):
    """Take action step"""
    data = await request.json()
    return proxy_request("/api/step", "POST", data)

@app.get("/api/state")
async def api_state():
    """Get current state"""
    return proxy_request("/api/state", "GET")

@app.get("/api/env/info")
async def api_env_info():
    """Get environment info"""
    return proxy_request("/api/env/info", "GET")

@app.get("/api/envs")
async def api_envs():
    """List environments"""
    return proxy_request("/api/envs", "GET")

@app.delete("/api/env/{env_id}")
async def api_delete_env(env_id: str):
    """Delete environment"""
    return proxy_request(f"/api/env/{env_id}", "DELETE")

def start_nodejs():
    """Start Node.js server"""
    try:
        process = subprocess.Popen(
            ["node", "index.js"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for startup
        time.sleep(3)
        
        # Test connection
        try:
            response = requests.get("http://localhost:7860/api/env/info", timeout=5)
            if response.status_code == 200:
                print("✅ Node.js server ready")
                return process
        except:
            pass
        
        process.terminate()
        return None
    except Exception as e:
        print(f"❌ Node.js error: {e}")
        return None

if __name__ == "__main__":
    print("🌍 Starting OpenEnv GridWorld Space...")
    
    # Start Node.js server
    node_process = start_nodejs()
    
    if node_process:
        print("🚀 Starting FastAPI server...")
        uvicorn.run(
            "inference:app",
            host="0.0.0.0",
            port=7860,
            log_level="info"
        )
        
        # Cleanup
        if node_process:
            node_process.terminate()
    else:
        print("❌ Failed to start Node.js server")
        print("Please ensure Node.js and index.js are available")