#!/usr/bin/env python3
"""
Hugging Face Inference Script for OpenEnv GridWorld
This script serves the OpenEnv web application on Hugging Face Spaces.
"""

import os
import subprocess
import time
import requests
from threading import Thread
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

app = FastAPI(title="OpenEnv GridWorld", description="Reinforcement Learning Environment")

# Mount static files
app.mount("/static", StaticFiles(directory="public"), name="static")

# Serve the main HTML file
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("public/index.html", "r") as f:
        return f.read()

@app.get("/about", response_class=HTMLResponse)
async def read_about():
    with open("public/about.html", "r") as f:
        return f.read()

@app.get("/home", response_class=HTMLResponse)
async def read_home():
    with open("public/home.html", "r") as f:
        return f.read()

# Proxy API endpoints to the Node.js server
@app.post("/api/reset")
async def api_reset(request: Request):
    return await proxy_to_nodejs("/api/reset", await request.json())

@app.post("/api/step")
async def api_step(request: Request):
    return await proxy_to_nodejs("/api/step", await request.json())

@app.get("/api/state")
async def api_state():
    return await proxy_to_nodejs("/api/state")

@app.get("/api/env/info")
async def api_env_info():
    return await proxy_to_nodejs("/api/env/info")

@app.get("/api/envs")
async def api_envs():
    return await proxy_to_nodejs("/api/envs")

@app.delete("/api/env/{env_id}")
async def api_delete_env(env_id: str):
    return await proxy_to_nodejs(f"/api/env/{env_id}", method="DELETE")

async def proxy_to_nodejs(path: str, data: dict = None, method: str = "POST"):
    """Proxy requests to the Node.js server"""
    nodejs_url = f"http://localhost:7860{path}"
    
    try:
        if method == "POST":
            response = requests.post(nodejs_url, json=data)
        elif method == "GET":
            response = requests.get(nodejs_url)
        elif method == "DELETE":
            response = requests.delete(nodejs_url)
        
        return response.json()
    except Exception as e:
        return {"error": str(e), "message": "Node.js server may not be running"}

def start_nodejs_server():
    """Start the Node.js server in a separate process"""
    try:
        # Start Node.js server
        process = subprocess.Popen(
            ["node", "index.js"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server started successfully
        try:
            response = requests.get("http://localhost:7860/api/env/info", timeout=5)
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

if __name__ == "__main__":
    # Start Node.js server in background
    nodejs_process = start_nodejs_server()
    
    if nodejs_process:
        print("🚀 Starting FastAPI server...")
        # Start FastAPI server
        uvicorn.run(
            "inference:app",
            host="0.0.0.0",
            port=7860,
            reload=False
        )
        
        # Cleanup
        if nodejs_process:
            nodejs_process.terminate()
    else:
        print("❌ Failed to start Node.js server. Please check your Node.js installation.")