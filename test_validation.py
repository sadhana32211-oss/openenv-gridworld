#!/usr/bin/env python3
"""
Test script to debug OpenEnv validation issues
"""

import os
import sys

def test_server_app_exists():
    """Test if server/app.py exists and is accessible"""
    print("Testing server/app.py accessibility...")
    
    # Test 1: Check if file exists
    if os.path.exists("server/app.py"):
        print("server/app.py exists")
    else:
        print("server/app.py does not exist")
        return False
    
    # Test 2: Check if we can import it
    try:
        sys.path.insert(0, os.path.abspath("."))
        import server.app
        print("server.app can be imported")
        
        # Test 3: Check if main function exists
        if hasattr(server.app, 'main'):
            print("server.app.main function exists")
        else:
            print("server.app.main function does not exist")
            
        # Test 4: Check if app object exists
        if hasattr(server.app, 'app'):
            print("server.app.app FastAPI object exists")
        else:
            print("server.app.app FastAPI object does not exist")
            
    except Exception as e:
        print(f"Cannot import server.app: {e}")
        return False
    
    return True

def test_pyproject_toml():
    """Test pyproject.toml configuration"""
    print("\nTesting pyproject.toml configuration...")
    
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            print("tomllib/tomli not available")
            return False
    
    try:
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
        
        # Check project.scripts
        if "project" in config and "scripts" in config["project"]:
            scripts = config["project"]["scripts"]
            if "server" in scripts:
                print(f"server script found: {scripts['server']}")
            else:
                print("server script not found in project.scripts")
        else:
            print("project.scripts not found in pyproject.toml")
            
        # Check dependencies
        if "project" in config and "dependencies" in config["project"]:
            deps = config["project"]["dependencies"]
            if any("openenv" in dep for dep in deps):
                print("openenv dependency found")
            else:
                print("openenv dependency not found")
        else:
            print("project.dependencies not found in pyproject.toml")
            
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("OpenEnv Validation Debug Test")
    print("=" * 40)
    
    test1 = test_server_app_exists()
    test2 = test_pyproject_toml()
    
    print("\n" + "=" * 40)
    if test1 and test2:
        print("All tests passed - validation should work")
    else:
        print("Some tests failed - validation issues detected")
