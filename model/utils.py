"""
Utility functions for image processing and aesthetic scoring.

This module provides utility functions for preprocessing images
and generating feedback based on aesthetic scores.

Copyright (c) 2025 Nicole LeGuern
Licensed under MIT License with attribution requirements
https://github.com/CodeQueenie/Aesthetic-Lens---AI_Powered_Image_Aesthetic_Scoring_Tool
"""

import logging
import numpy as np
from PIL import Image
import tensorflow as tf

# Import configuration settings
from config import MODEL_SETTINGS

logger = logging.getLogger(__name__)

def preprocess_image(image_path, target_size=None):
    """
    Preprocess an image for the NIMA model.
    
    Args:
        image_path (str): Path to the image file
        target_size (tuple): Target size for the image (height, width)
        
    Returns:
        numpy.ndarray: Preprocessed image as a numpy array
        
    Raises:
        Exception: If image preprocessing fails
    """
    try:
        # Use the target size from configuration if not specified
        if target_size is None:
            target_size = MODEL_SETTINGS["input_shape"][:2]  # Get height and width from input_shape
        
        # Load the image
        logger.info(f"Loading image from {image_path}")
        img = Image.open(image_path).convert("RGB")
        
        # Resize the image
        img = img.resize(target_size, Image.LANCZOS)
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Normalize pixel values to [0, 1]
        img_array = img_array / 255.0
        
        # Ensure the array has the right shape
        if len(img_array.shape) != 3:
            raise ValueError(f"Invalid image shape: {img_array.shape}")
        
        logger.info(f"Image preprocessed successfully: {img_array.shape}")
        return img_array
    except Exception as e:
        logger.error(f"Failed to preprocess image: {str(e)}")
        raise

def get_feedback_from_score(score):
    """
    Generate feedback based on the aesthetic score.
    
    Args:
        score (float): Aesthetic score between 1 and 10
        
    Returns:
        str: Feedback message based on the score
    """
    try:
        if score < 3:
            return "This image has significant aesthetic issues. Consider improving composition, lighting, and subject matter."
        elif score < 5:
            return "This image has below-average aesthetic quality. There's room for improvement in composition and visual appeal."
        elif score < 7:
            return "This image has average aesthetic quality. It's decent but could be enhanced with better composition or lighting."
        elif score < 9:
            return "This image has good aesthetic quality. It demonstrates strong composition and visual appeal."
        else:
            return "This image has excellent aesthetic quality. It showcases exceptional composition, lighting, and visual appeal."
    except Exception as e:
        logger.error(f"Failed to generate feedback: {str(e)}")
        return "Unable to generate feedback for this score."

def create_heatmap(model, image, layer_name="dense_1"):
    """
    Create a heatmap highlighting the regions that contribute to the aesthetic score.
    
    Args:
        model: The NIMA model
        image (numpy.ndarray): Preprocessed image as a numpy array
        layer_name (str): Name of the layer to use for the heatmap
        
    Returns:
        numpy.ndarray: Heatmap as a numpy array
        
    Raises:
        Exception: If heatmap creation fails
    """
    try:
        # Ensure image has the right shape
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        
        # Create a model that maps the input image to the activations
        # of the last conv layer as well as the output predictions
        grad_model = tf.keras.models.Model(
            [model.inputs],
            [model.get_layer(layer_name).output, model.output]
        )
        
        # Compute the gradient of the top predicted class for our input image
        # with respect to the activations of the last conv layer
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(image)
            top_pred_index = tf.argmax(predictions[0])
            top_class_channel = predictions[:, top_pred_index]
        
        # This is the gradient of the output neuron with respect to
        # the output feature map of the last conv layer
        grads = tape.gradient(top_class_channel, conv_outputs)
        
        # Vector of mean intensity of the gradient over a specific feature map channel
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Weight the channels by the gradient values
        conv_outputs = conv_outputs[0]
        heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs), axis=-1)
        
        # Normalize the heatmap
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
        
        # Convert to numpy array
        heatmap = heatmap.numpy()
        
        logger.info("Heatmap created successfully")
        return heatmap
    except Exception as e:
        logger.error(f"Failed to create heatmap: {str(e)}")
        raise
