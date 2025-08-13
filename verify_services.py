#!/usr/bin/env python3

import requests
import json
import sys

def check_backend():
    """Check if backend is running and healthy."""
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend is healthy: {data}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def check_frontend():
    """Check if frontend is accessible."""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✓ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=== CGSRef Service Verification ===")
    
    backend_ok = check_backend()
    frontend_ok = check_frontend()
    
    print("\n=== Summary ===")
    print(f"Backend (API): {'✓ Running on port 8002' if backend_ok else '❌ Not accessible'}")
    print(f"Frontend (React): {'✓ Running on port 3000' if frontend_ok else '❌ Not accessible'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 All services are running correctly!")
        print("You can access:")
        print("  - Frontend: http://localhost:3000")
        print("  - API Docs: http://localhost:8002/docs")
        print("  - Health Check: http://localhost:8002/health")
    else:
        print("\n⚠️  Some services are not working properly.")
        sys.exit(1)
