"""
Demo script for the NIMA model

This script demonstrates the NIMA model by loading a sample image and predicting its aesthetic score.
"""

import os
import sys
import logging
import argparse
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# Import model-related modules
from model.nima_model import NimaModel
from model.utils import preprocess_image, get_feedback_from_score
from config import MODEL_SETTINGS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to demonstrate the NIMA model.
    """
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="Demo the NIMA model with a sample image")
        parser.add_argument("--image", type=str, required=True, help="Path to the image file")
        args = parser.parse_args()
        
        # Check if the image file exists
        if not os.path.exists(args.image):
            logger.error(f"Image file not found: {args.image}")
            sys.exit(1)
        
        # Load and preprocess the image
        logger.info(f"Loading image: {args.image}")
        preprocessed_image = preprocess_image(args.image)
        
        # Initialize the NIMA model
        logger.info("Initializing NIMA model...")
        model = NimaModel()
        
        # Predict the aesthetic score
        logger.info("Predicting aesthetic score...")
        score = model.predict(preprocessed_image)
        
        # Get feedback based on the score
        feedback = get_feedback_from_score(score)
        
        # Display the results
        logger.info(f"Aesthetic score: {score}/10")
        logger.info(f"Feedback: {feedback}")
        
        # Display the image with the score
        display_results(args.image, score, feedback)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

def display_results(image_path, score, feedback):
    """
    Display the image with its aesthetic score and feedback.
    
    Args:
        image_path (str): Path to the image file
        score (float): Aesthetic score
        feedback (str): Feedback based on the score
    """
    try:
        # Load the image
        img = Image.open(image_path)
        
        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Display the image
        ax1.imshow(np.array(img))
        ax1.set_title("Input Image")
        ax1.axis("off")
        
        # Display the score as a gauge
        create_score_gauge(ax2, score)
        
        # Add feedback as text
        plt.figtext(0.5, 0.01, feedback, ha="center", fontsize=12, 
                   bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 5})
        
        # Adjust layout and display
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)
        plt.show()
        
    except Exception as e:
        logger.error(f"Failed to display results: {str(e)}")

def create_score_gauge(ax, score):
    """
    Create a gauge visualization for the aesthetic score.
    
    Args:
        ax (matplotlib.axes.Axes): Matplotlib axes to draw on
        score (float): Aesthetic score
    """
    # Define colors for different score ranges
    colors = [(0.8, 0.2, 0.2), (0.8, 0.8, 0.2), (0.2, 0.8, 0.2)]
    
    # Create a gauge-like visualization
    ax.set_aspect("equal")
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    
    # Draw the gauge background
    theta = np.linspace(0, 180, 100) * np.pi / 180
    x = np.cos(theta)
    y = np.sin(theta)
    ax.plot(x, y, color="black", linewidth=3)
    
    # Draw tick marks
    for i in range(1, 11):
        angle = i * 18 * np.pi / 180
        x_tick = 0.9 * np.cos(angle)
        y_tick = 0.9 * np.sin(angle)
        ax.plot([0.9 * np.cos(angle), np.cos(angle)], 
                [0.9 * np.sin(angle), np.sin(angle)], 
                color="black", linewidth=1)
        ax.text(1.05 * np.cos(angle), 1.05 * np.sin(angle), 
                str(i), ha="center", va="center")
    
    # Draw the needle
    score_angle = score * 18 * np.pi / 180
    ax.plot([0, 0.8 * np.cos(score_angle)], [0, 0.8 * np.sin(score_angle)], 
            color="red", linewidth=3)
    
    # Add a center dot
    ax.add_patch(plt.Circle((0, 0), 0.05, color="black"))
    
    # Add the score text
    ax.text(0, -0.5, f"Score: {score}/10", ha="center", va="center", 
            fontsize=16, fontweight="bold")
    
    # Remove axis ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Aesthetic Score", fontsize=14)

if __name__ == "__main__":
    main()
