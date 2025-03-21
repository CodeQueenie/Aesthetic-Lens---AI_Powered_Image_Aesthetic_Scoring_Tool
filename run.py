"""
Run script for the Aesthetic Lens application

This script provides a simple way to run the Aesthetic Lens application.
"""

import os
import sys
import logging
from app import app
from config import PORT, DEBUG

if __name__ == "__main__":
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.StreamHandler()
            ]
        )
        logger = logging.getLogger(__name__)
        
        # Log startup information
        logger.info("Starting Aesthetic Lens application...")
        logger.info(f"Debug mode: {DEBUG}")
        logger.info(f"Port: {PORT}")
        
        # Run the Flask application
        app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
    except Exception as e:
        print(f"Error starting application: {str(e)}", file=sys.stderr)
        sys.exit(1)
