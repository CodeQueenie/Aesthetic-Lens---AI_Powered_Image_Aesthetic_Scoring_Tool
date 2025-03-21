"""
Aesthetic Lens - Main Flask Application

This module serves as the main entry point for the Aesthetic Lens application,
handling HTTP requests, image uploads, and rendering HTML templates.

Copyright (c) 2025 Nicole LeGuern
Licensed under MIT License with attribution requirements
https://github.com/CodeQueenie/Aesthetic-Lens---AI_Powered_Image_Aesthetic_Scoring_Tool
"""

import os
import logging
import json
import shutil
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import uuid
import datetime

# Import configuration settings
from config import (
    UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH,
    SECRET_KEY, DEBUG, PORT, LOG_FILE, LOG_FORMAT
)

# Import model-related modules
from model.nima_model import NimaModel
from model.utils import preprocess_image, get_feedback_from_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configure upload folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize NIMA model
try:
    nima_model = NimaModel()
    logger.info("NIMA model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize NIMA model: {str(e)}")
    nima_model = None


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): Name of the uploaded file
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """
    Render the main page of the application.
    
    Returns:
        str: Rendered HTML template for the index page
    """
    return render_template("index.html")


@app.route("/examples")
def examples():
    """
    Render the examples page showing images with different score ranges.
    
    Returns:
        str: Rendered HTML template for the examples page
    """
    # Initialize example images for each category
    example_images = {
        "low": [],
        "average": [],
        "high": [],
        "excellent": []
    }
    
    # Path to examples directory and metadata file
    examples_dir = os.path.join("static", "images", "examples")
    metadata_file = os.path.join(examples_dir, "examples_metadata.json")
    
    # Load metadata if available
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                
            # Process each example image
            for filename, data in metadata.items():
                # Skip if file doesn't exist
                if not os.path.exists(os.path.join(examples_dir, filename)):
                    continue
                    
                # Determine category based on filename prefix
                if filename.startswith("low_score_"):
                    category = "low"
                elif filename.startswith("average_score_"):
                    category = "average"
                elif filename.startswith("high_score_"):
                    category = "high"
                elif filename.startswith("excellent_score_"):
                    category = "excellent"
                else:
                    continue
                
                # Add to appropriate category
                example_images[category].append({
                    "filename": filename,
                    "score": data.get("score", 0.0),
                    "description": data.get("description", ""),
                    "contributor": data.get("contributor", "Anonymous")
                })
                
            # Sort examples by score within each category
            for category in example_images:
                example_images[category] = sorted(example_images[category], key=lambda x: x["score"])
                
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading example metadata: {str(e)}")
    
    return render_template("examples.html", example_images=example_images)


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Handle image upload and processing.
    
    Returns:
        str: Rendered HTML template with the aesthetic score result
    """
    try:
        # Debug information
        logger.info(f"Form data: {request.form}")
        logger.info(f"Files: {request.files}")
        
        # Check if the post request has the file part
        if "file" not in request.files:
            logger.error("No file part in the request")
            flash("No file part")
            return redirect(url_for("index"))
            
        file = request.files["file"]
        logger.info(f"Received file: {file.filename}")
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            logger.error("No selected file")
            flash("No selected file")
            return redirect(url_for("index"))
            
        if file and allowed_file(file.filename):
            # Secure the filename to prevent security issues
            filename = secure_filename(file.filename)
            
            # Generate a unique filename to avoid overwriting
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            
            # Save the uploaded file
            file.save(filepath)
            logger.info(f"File saved: {filepath}")
            
            # Process the image and get the aesthetic score
            if nima_model:
                try:
                    # Preprocess the image for the model
                    preprocessed_image = preprocess_image(filepath)
                    
                    # Get the aesthetic score from the model
                    score = nima_model.predict(preprocessed_image)
                    
                    # Get feedback based on the score
                    feedback = get_feedback_from_score(score)
                    
                    logger.info(f"Image processed. Score: {score}")
                    
                    # Redirect to the result page with the filename as a query parameter
                    return redirect(url_for("result", filename=unique_filename))
                except Exception as e:
                    logger.error(f"Error processing image: {str(e)}")
                    flash(f"Error processing image: {str(e)}")
                    return redirect(url_for("index"))
            else:
                flash("Model not available. Please try again later.")
                return redirect(url_for("index"))
        else:
            flash("File type not allowed. Please upload a JPG, JPEG, or PNG image.")
            return redirect(url_for("index"))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        flash(f"An unexpected error occurred: {str(e)}")
        return redirect(url_for("index"))


@app.route("/result")
def result():
    """
    Display the result page with the aesthetic score and feedback.
    
    Returns:
        str: Rendered HTML template with the score and feedback
    """
    try:
        # Get the filename from the query parameters
        filename = request.args.get("filename")
        
        if not filename:
            logger.error("No filename provided in request")
            return redirect(url_for("index"))
        
        # Get the full path to the uploaded file
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return redirect(url_for("index"))
        
        # Load the model if not already loaded
        if not hasattr(app, "model"):
            logger.info("Loading NIMA model...")
            app.model = NimaModel()
        
        # Preprocess the image
        preprocessed_image = preprocess_image(file_path)
        
        # Predict the aesthetic score
        score = app.model.predict(preprocessed_image)
        
        # Get feedback based on the score
        feedback = get_feedback_from_score(score)
        
        logger.info(f"Aesthetic score for {filename}: {score}")
        
        # Render the result template with the score and feedback
        return render_template(
            "result.html", 
            filename=filename, 
            score=score, 
            feedback=feedback
        )
    except Exception as e:
        logger.error(f"Error displaying result: {str(e)}")
        return render_template("500.html"), 500


@app.route("/api/score", methods=["POST"])
def api_score():
    """
    API endpoint for scoring images.
    
    Returns:
        dict: JSON response with the aesthetic score and feedback
    """
    try:
        # Check if the post request has the file part
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files["file"]
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
            
        if file and allowed_file(file.filename):
            # Secure the filename to prevent security issues
            filename = secure_filename(file.filename)
            
            # Generate a unique filename to avoid overwriting
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            
            # Save the uploaded file
            file.save(filepath)
            logger.info(f"API: File saved: {filepath}")
            
            # Process the image and get the aesthetic score
            if nima_model:
                try:
                    # Preprocess the image for the model
                    preprocessed_image = preprocess_image(filepath)
                    
                    # Get the aesthetic score from the model
                    score = nima_model.predict(preprocessed_image)
                    
                    # Get feedback based on the score
                    feedback = get_feedback_from_score(score)
                    
                    logger.info(f"API: Image processed. Score: {score}")
                    
                    # Return the score and feedback as JSON
                    return jsonify({
                        "filename": unique_filename,
                        "score": score,
                        "feedback": feedback
                    })
                except Exception as e:
                    logger.error(f"API: Error processing image: {str(e)}")
                    return jsonify({"error": f"Error processing image: {str(e)}"}), 500
            else:
                return jsonify({"error": "Model not available. Please try again later."}), 503
        else:
            return jsonify({"error": "File type not allowed. Please upload a JPG, JPEG, or PNG image."}), 400
    except Exception as e:
        logger.error(f"API: Unexpected error: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route("/contribute-example", methods=["POST"])
def contribute_example():
    """
    Handle user contributions of example images.
    
    Returns:
        str: Redirect to examples page with a success message
    """
    try:
        # Get form data
        filename = request.form.get("filename")
        score = float(request.form.get("score"))
        contributor_name = request.form.get("contributor_name", "Anonymous")
        image_description = request.form.get("image_description", "")
        
        # Validate data
        if not filename or not os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], filename)):
            flash("Invalid image file.")
            return redirect(url_for("examples"))
            
        # Determine the score range category
        if score < 4.0:
            category = "low"
        elif score < 7.0:
            category = "average"
        elif score < 9.0:
            category = "high"
        else:
            category = "excellent"
            
        # Create examples directory if it doesn't exist
        examples_dir = os.path.join("static", "images", "examples")
        if not os.path.exists(examples_dir):
            os.makedirs(examples_dir)
            
        # Count existing examples in this category to determine the next number
        existing_files = [f for f in os.listdir(examples_dir) 
                         if f.startswith(f"{category}_score_") and f.endswith((".jpg", ".jpeg", ".png"))]
        next_number = len(existing_files) + 1
        
        # Create a new filename for the example
        source_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file_ext = os.path.splitext(filename)[1].lower()
        new_filename = f"{category}_score_{next_number}{file_ext}"
        target_path = os.path.join(examples_dir, new_filename)
        
        # Copy the file to the examples directory
        shutil.copy2(source_path, target_path)
        
        # Save metadata about the example
        metadata_file = os.path.join(examples_dir, "examples_metadata.json")
        metadata = {}
        
        # Load existing metadata if available
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
            except json.JSONDecodeError:
                metadata = {}
        
        # Add new example metadata
        metadata[new_filename] = {
            "score": score,
            "contributor": contributor_name,
            "description": image_description,
            "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save updated metadata
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=4)
            
        flash("Thank you for contributing your image as an example!")
        return redirect(url_for("examples"))
        
    except Exception as e:
        logger.error(f"Error contributing example: {str(e)}")
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for("examples"))


@app.route("/admin/examples")
def admin_examples():
    """
    Admin interface for managing example images.
    
    Returns:
        str: Rendered HTML template for the admin examples page
    """
    # Initialize example images for each category
    example_images = {
        "low": [],
        "average": [],
        "high": [],
        "excellent": []
    }
    
    # Path to examples directory and metadata file
    examples_dir = os.path.join("static", "images", "examples")
    metadata_file = os.path.join(examples_dir, "examples_metadata.json")
    
    # Load metadata if available
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                
            # Process each example image
            for filename, data in metadata.items():
                # Skip if file doesn't exist
                if not os.path.exists(os.path.join(examples_dir, filename)):
                    continue
                    
                # Determine category based on filename prefix
                if filename.startswith("low_score_"):
                    category = "low"
                elif filename.startswith("average_score_"):
                    category = "average"
                elif filename.startswith("high_score_"):
                    category = "high"
                elif filename.startswith("excellent_score_"):
                    category = "excellent"
                else:
                    continue
                
                # Add to appropriate category
                example_images[category].append({
                    "filename": filename,
                    "score": data.get("score", 0.0),
                    "description": data.get("description", ""),
                    "contributor": data.get("contributor", "Anonymous")
                })
                
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading example metadata: {str(e)}")
    
    return render_template("admin_examples.html", example_images=example_images)


@app.route("/admin/add-example", methods=["POST"])
def admin_add_example():
    """
    Handle admin uploads of example images.
    
    Returns:
        str: Redirect to admin examples page with a success message
    """
    try:
        # Check if the post request has the file part
        if "example_image" not in request.files:
            flash("No file part")
            return redirect(url_for("admin_examples"))
            
        file = request.files["example_image"]
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("No selected file")
            return redirect(url_for("admin_examples"))
            
        if file and allowed_file(file.filename):
            # Get form data
            category = request.form.get("category")
            score = float(request.form.get("score"))
            description = request.form.get("description", "")
            contributor = request.form.get("contributor", "Admin")
            
            # Validate category
            if category not in ["low", "average", "high", "excellent"]:
                flash("Invalid category")
                return redirect(url_for("admin_examples"))
                
            # Create examples directory if it doesn't exist
            examples_dir = os.path.join("static", "images", "examples")
            if not os.path.exists(examples_dir):
                os.makedirs(examples_dir)
                
            # Count existing examples in this category to determine the next number
            existing_files = [f for f in os.listdir(examples_dir) 
                             if f.startswith(f"{category}_score_") and f.endswith((".jpg", ".jpeg", ".png"))]
            next_number = len(existing_files) + 1
            
            # Create a new filename for the example
            file_ext = os.path.splitext(file.filename)[1].lower()
            new_filename = f"{category}_score_{next_number}{file_ext}"
            target_path = os.path.join(examples_dir, new_filename)
            
            # Save the file
            file.save(target_path)
            
            # Save metadata about the example
            metadata_file = os.path.join(examples_dir, "examples_metadata.json")
            metadata = {}
            
            # Load existing metadata if available
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                except json.JSONDecodeError:
                    metadata = {}
            
            # Add new example metadata
            metadata[new_filename] = {
                "score": score,
                "contributor": contributor,
                "description": description,
                "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save updated metadata
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=4)
                
            flash("Example image added successfully!")
            return redirect(url_for("admin_examples"))
        else:
            flash("File type not allowed")
            return redirect(url_for("admin_examples"))
            
    except Exception as e:
        logger.error(f"Error adding example: {str(e)}")
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for("admin_examples"))


@app.route("/delete-example", methods=["POST"])
def delete_example():
    """
    Delete an example image.
    
    Returns:
        str: Redirect to admin examples page with a success message
    """
    try:
        # Get filename from form
        filename = request.form.get("filename")
        
        if not filename:
            flash("No filename provided")
            return redirect(url_for("admin_examples"))
            
        # Path to examples directory and metadata file
        examples_dir = os.path.join("static", "images", "examples")
        metadata_file = os.path.join(examples_dir, "examples_metadata.json")
        file_path = os.path.join(examples_dir, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            flash("File not found")
            return redirect(url_for("admin_examples"))
            
        # Delete the file
        os.remove(file_path)
        
        # Update metadata
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    
                # Remove the entry from metadata
                if filename in metadata:
                    del metadata[filename]
                    
                # Save updated metadata
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=4)
                    
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error updating metadata: {str(e)}")
        
        flash("Example image deleted successfully!")
        return redirect(url_for("admin_examples"))
        
    except Exception as e:
        logger.error(f"Error deleting example: {str(e)}")
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for("admin_examples"))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """
    Serve uploaded files.
    
    Args:
        filename (str): Name of the file to serve
        
    Returns:
        Response: The requested file
    """
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 errors.
    
    Args:
        e: The error
        
    Returns:
        tuple: Rendered 404 template and status code
    """
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    """
    Handle 500 errors.
    
    Args:
        e: The error
        
    Returns:
        tuple: Rendered 500 template and status code
    """
    logger.error(f"Server error: {str(e)}")
    return render_template("500.html"), 500


if __name__ == "__main__":
    # Run the Flask application
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
    logger.info(f"Application started on port {PORT}")
