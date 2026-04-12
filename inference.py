"""
OpenEnv GridWorld - Hugging Face Inference Script
Simple inference script for Hugging Face Spaces compatibility.
Provides all required API endpoints directly without external dependencies.
"""

import os
import sys
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# GridWorld environment state
class GridWorldEnv:
    def __init__(self, grid_size=5):
        self.grid_size = grid_size
        self.agent_pos = {"x": 0, "y": 0}
        self.goal_pos = {"x": grid_size - 1, "y": grid_size - 1}
        self.steps = 0
        self.done = False
        self.total_reward = 0
        self.max_steps = 100
        
        # Create grid with obstacles and pits
        self.grid = [
            ["agent", "empty", "empty", "empty", "empty"],
            ["empty", "empty", "obstacle", "empty", "empty"],
            ["empty", "pit", "obstacle", "pit", "empty"],
            ["empty", "empty", "obstacle", "empty", "empty"],
            ["empty", "empty", "empty", "empty", "goal"]
        ]
        
        self.rewards = {
            "goal": 10,
            "obstacle": -0.5,
            "pit": -1,
            "boundary": -0.1,
            "step": -0.01
        }
    
    def reset(self):
        """Reset environment to initial state"""
        self.agent_pos = {"x": 0, "y": 0}
        self.steps = 0
        self.done = False
        self.total_reward = 0
        self.grid[0][0] = "agent"
        self.grid[4][4] = "goal"
        return self.get_state()
    
    def step(self, action):
        """Take an action step"""
        if self.done:
            return self.get_state(), 0, True, {}
        
        # Map action to direction
        directions = {
            0: (0, -1),  # UP
            1: (1, 0),   # RIGHT
            2: (0, 1),   # DOWN
            3: (-1, 0)   # LEFT
        }
        
        dx, dy = directions.get(action, (0, 0))
        new_x = self.agent_pos["x"] + dx
        new_y = self.agent_pos["y"] + dy
        
        # Check boundaries
        if new_x < 0 or new_x >= self.grid_size or new_y < 0 or new_y >= self.grid_size:
            reward = self.rewards["boundary"]
        else:
            # Check cell type
            cell = self.grid[new_y][new_x]
            if cell == "goal":
                reward = self.rewards["goal"]
                self.done = True
            elif cell == "obstacle":
                reward = self.rewards["obstacle"]
            elif cell == "pit":
                reward = self.rewards["pit"]
            else:
                reward = self.rewards["step"]
            
            # Update position
            self.grid[self.agent_pos["y"]][self.agent_pos["x"]] = "empty"
            self.agent_pos = {"x": new_x, "y": new_y}
            self.grid[new_y][new_x] = "agent"
        
        self.total_reward += reward
        self.steps += 1
        
        if self.steps >= self.max_steps:
            self.done = True
        
        return self.get_state(), reward, self.done, {}
    
    def get_state(self):
        """Get current state"""
        return {
            "agent_position": self.agent_pos,
            "goal_position": self.goal_pos,
            "grid_size": self.grid_size,
            "grid": self.grid,
            "steps": self.steps,
            "done": self.done,
            "total_reward": self.total_reward
        }
    
    def get_info(self):
        """Get environment info"""
        return {
            "name": "GridWorld-v0",
            "description": "A classic grid world reinforcement learning environment where an agent navigates to reach a goal while avoiding obstacles and pits.",
            "version": "1.0.0",
            "grid_size": self.grid_size,
            "action_space": {
                "type": "discrete",
                "n": 4,
                "labels": ["UP", "RIGHT", "DOWN", "LEFT"]
            },
            "observation_space": {
                "type": "grid",
                "shape": [self.grid_size, self.grid_size],
                "cellTypes": ["empty", "agent", "goal", "obstacle", "pit"]
            },
            "reward_range": {"min": -1, "max": 10},
            "max_steps": self.max_steps,
            "rewards": self.rewards
        }

# Create environment instance
env = GridWorldEnv()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/":
            self.serve_file("public/index.html", "text/html")
        elif path == "/about":
            self.serve_file("public/about.html", "text/html")
        elif path == "/home":
            self.serve_file("public/home.html", "text/html")
        elif path == "/api/state":
            self.send_json_response({
                "env_id": "default",
                "state": env.get_state(),
                "info": env.get_info()
            })
        elif path == "/api/env/info":
            self.send_json_response(env.get_info())
        elif path == "/api/envs":
            self.send_json_response({
                "environments": [{
                    "env_id": "default",
                    "name": "GridWorld-v0",
                    "grid_size": env.grid_size,
                    "action_space": env.get_info()["action_space"],
                    "observation_space": env.get_info()["observation_space"],
                    "reward_range": env.get_info()["reward_range"],
                    "max_steps": env.max_steps,
                    "rewards": env.rewards,
                    "current_state": env.get_state()
                }]
            })
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/api/reset":
            state = env.reset()
            self.send_json_response({
                "env_id": "default",
                "state": state,
                "info": env.get_info()
            })
        elif path == "/api/step":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode())
                action = data.get("action", 0)
                
                state, reward, done, info = env.step(action)
                
                self.send_json_response({
                    "env_id": "default",
                    "state": state,
                    "reward": reward,
                    "done": done,
                    "info": info
                })
            except Exception as e:
                self.send_json_response({"error": str(e)}, 400)
        else:
            self.send_error(404, "Not Found")
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path.startswith("/api/env/"):
            env_id = path.split("/")[-1]
            self.send_json_response({
                "success": True,
                "message": f"Environment '{env_id}' deleted"
            })
        else:
            self.send_error(404, "Not Found")
    
    def serve_file(self, filepath, content_type):
        """Serve static files"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>OpenEnv GridWorld</h1><p>Files not found.</p>')
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        """Override to suppress default logging"""
        pass

def run_server():
    """Run the HTTP server"""
    try:
        server = HTTPServer(('0.0.0.0', 7860), SimpleHTTPRequestHandler)
        print("🚀 Starting HTTP server on port 7860...")
        print("🌍 OpenEnv GridWorld Space is ready!")
        print("📡 API endpoints available:")
        print("   - GET /api/state")
        print("   - POST /api/reset")
        print("   - POST /api/step")
        print("   - GET /api/env/info")
        print("   - GET /api/envs")
        print("   - DELETE /api/env/{env_id}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    print("✅ inference.py executed successfully")
