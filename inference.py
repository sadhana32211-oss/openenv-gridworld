#!/usr/bin/env python3
"""
OpenEnv GridWorld - Hugging Face Inference Script
Simple inference script for Hugging Face Spaces compatibility.
"""

import os
import sys
import subprocess
import time

# Simple HTTP server using built-in modules
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
    import json
    import socket
    print("✅ Using built-in HTTP server")
except ImportError:
    print("❌ Failed to import required modules")
    sys.exit(1)

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
            self.proxy_to_nodejs("/api/state", "GET")
        elif path == "/api/env/info":
            self.proxy_to_nodejs("/api/env/info", "GET")
        elif path == "/api/envs":
            self.proxy_to_nodejs("/api/envs", "GET")
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/api/reset":
            self.proxy_to_nodejs("/api/reset", "POST")
        elif path == "/api/step":
            self.proxy_to_nodejs("/api/step", "POST")
        else:
            self.send_error(404, "Not Found")
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path.startswith("/api/env/"):
            self.proxy_to_nodejs(path, "DELETE")
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
            self.send_error(404, "File Not Found")
    
    def proxy_to_nodejs(self, path, method):
        """Proxy requests to Node.js server"""
        try:
            # Simple socket-based proxy
            import socket
            
            # Connect to Node.js server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 7860))
            
            # Build HTTP request
            if method == "POST":
                content_length = int(self.headers.get('Content-Length', 0))
                data = self.rfile.read(content_length)
                request_body = data.decode()
                
                request = f"{method} {path} HTTP/1.1\r\n"
                request += f"Host: localhost:7860\r\n"
                request += f"Content-Type: application/json\r\n"
                request += f"Content-Length: {len(request_body)}\r\n"
                request += "Connection: close\r\n"
                request += "\r\n"
                request += request_body
            else:
                request = f"{method} {path} HTTP/1.1\r\n"
                request += "Host: localhost:7860\r\n"
                request += "Connection: close\r\n"
                request += "\r\n"
            
            # Send request
            sock.send(request.encode())
            
            # Receive response
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            sock.close()
            
            # Parse response
            response_str = response.decode()
            headers, body = response_str.split('\r\n\r\n', 1)
            
            # Send response to client
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(body.encode())
            
        except Exception as e:
            error_response = {"error": str(e), "message": "Node.js server may not be running"}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

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
        time.sleep(5)
        
        # Test connection
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 7860))
            sock.close()
            
            if result == 0:
                print("✅ Node.js server ready")
                return process
        except:
            pass
        
        process.terminate()
        return None
    except Exception as e:
        print(f"❌ Node.js error: {e}")
        return None

def run_server():
    """Run the HTTP server"""
    try:
        server = HTTPServer(('0.0.0.0', 7860), SimpleHTTPRequestHandler)
        print("🚀 Starting HTTP server on port 7860...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    print("🌍 Starting OpenEnv GridWorld Space...")
    
    # Start Node.js server
    node_process = start_nodejs()
    
    if node_process:
        try:
            run_server()
        finally:
            # Cleanup
            if node_process:
                node_process.terminate()
    else:
        print("❌ Failed to start Node.js server")
        print("Please ensure Node.js and index.js are available")
