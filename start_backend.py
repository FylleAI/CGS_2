#!/usr/bin/env python3

import sys
import os
import uvicorn
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the app
from api.rest.main import app

if __name__ == "__main__":
    print("Starting CGSRef Backend...")
    print("Logs will show detailed information about requests")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=False,
        timeout_keep_alive=600,  # 10 minutes keep-alive for long workflows
        timeout_graceful_shutdown=30  # 30 seconds graceful shutdown
    )
