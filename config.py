"""
Configuration settings for the Aesthetic Lens application.

This module contains configuration settings for the Aesthetic Lens application,
including paths, model settings, and application parameters.

Copyright (c) 2025 Nicole LeGuern
Licensed under MIT License with attribution requirements
https://github.com/CodeQueenie/Aesthetic-Lens---AI_Powered_Image_Aesthetic_Scoring_Tool
"""

import os
import uuid

# Base directory of the application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload folder configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

# Flask application configuration
SECRET_KEY = os.environ.get("SECRET_KEY", str(uuid.uuid4()))
DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
PORT = int(os.environ.get("PORT", 5000))

# Model configuration
MODEL_SETTINGS = {
    "input_shape": (224, 224, 3),
    "mobilenet_url": "https://tfhub.dev/google/tf2-preview/mobilenet_v2/feature_vector/4",
}

# Logging configuration
LOG_FILE = os.path.join(BASE_DIR, "aesthetic_lens.log")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

# Create necessary directories if they don't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
