"""
NIMA (Neural Image Assessment) Model Implementation

This module implements the NIMA model for aesthetic scoring of images
using TensorFlow and a pre-trained MobileNet model.

Copyright (c) 2025 Nicole LeGuern
Licensed under MIT License with attribution requirements
https://github.com/CodeQueenie/Aesthetic-Lens---AI_Powered_Image_Aesthetic_Scoring_Tool
"""

import os
import logging
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

# Import configuration settings
from config import MODEL_SETTINGS

logger = logging.getLogger(__name__)

class NimaModel:
    """
    NIMA model for aesthetic image scoring.
    
    This class implements the Neural Image Assessment model using
    a pre-trained MobileNet model from TensorFlow Hub.
    """
    
    def __init__(self):
        """
        Initialize the NIMA model.
        
        Loads the pre-trained MobileNet model and sets up the scoring layers.
        
        Raises:
            Exception: If model loading fails
        """
        try:
            # Load the MobileNet model from TensorFlow Hub
            logger.info("Loading MobileNet model from TensorFlow Hub...")
            mobilenet_url = MODEL_SETTINGS["mobilenet_url"]
            input_shape = MODEL_SETTINGS["input_shape"]
            self.base_model = hub.KerasLayer(mobilenet_url, input_shape=input_shape)
            
            # Freeze the base model
            self.base_model.trainable = False
            
            # Build the NIMA model on top of MobileNet
            logger.info("Building NIMA model...")
            self._build_model()
            
            logger.info("NIMA model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NIMA model: {str(e)}")
            raise
    
    def _build_model(self):
        """
        Build the NIMA model architecture.
        
        Creates a model that takes an image as input and outputs an aesthetic score.
        """
        try:
            # Input layer
            inputs = tf.keras.Input(shape=MODEL_SETTINGS["input_shape"])
            
            # Feature extraction with MobileNet
            x = self.base_model(inputs)
            
            # Add dropout to prevent overfitting
            x = tf.keras.layers.Dropout(0.5)(x)
            
            # Add dense layers
            x = tf.keras.layers.Dense(256, activation="relu")(x)
            x = tf.keras.layers.Dropout(0.5)(x)
            x = tf.keras.layers.Dense(128, activation="relu")(x)
            
            # Output layer for aesthetic score (1-10)
            # We use 10 outputs for scores 1-10 and apply softmax
            x = tf.keras.layers.Dense(10, activation="softmax")(x)
            
            # Create the model
            self.model = tf.keras.Model(inputs=inputs, outputs=x)
            
            # Since we're using a pre-trained model and not training,
            # we don't need to compile it with loss and optimizer
            # But we'll do it anyway for completeness
            self.model.compile(
                optimizer="adam",
                loss="categorical_crossentropy",
                metrics=["accuracy"]
            )
            
            logger.info("NIMA model built successfully")
        except Exception as e:
            logger.error(f"Failed to build NIMA model: {str(e)}")
            raise
    
    def predict(self, image):
        """
        Predict the aesthetic score for an image.
        
        Args:
            image (numpy.ndarray): Preprocessed image as a numpy array
            
        Returns:
            float: Aesthetic score between 1 and 10
            
        Raises:
            Exception: If prediction fails
        """
        try:
            # Ensure image has the right shape
            if len(image.shape) == 3:
                image = np.expand_dims(image, axis=0)
            
            # Get the predicted scores (probabilities for each score from 1-10)
            predictions = self.model.predict(image)
            
            # Calculate the mean score
            # The score is a weighted average where the weights are 1-10
            # and the probabilities are the predicted values
            score_weights = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            mean_score = np.sum(predictions[0] * score_weights)
            
            # Round to 2 decimal places
            mean_score = round(float(mean_score), 2)
            
            logger.info(f"Predicted aesthetic score: {mean_score}")
            return mean_score
        except Exception as e:
            logger.error(f"Failed to predict aesthetic score: {str(e)}")
            raise
    
    def _load_weights(self, weights_path):
        """
        Load pre-trained weights for the NIMA model.
        
        Args:
            weights_path (str): Path to the weights file
            
        Raises:
            Exception: If loading weights fails
        """
        try:
            if os.path.exists(weights_path):
                logger.info(f"Loading weights from {weights_path}")
                self.model.load_weights(weights_path)
                logger.info("Weights loaded successfully")
            else:
                logger.warning(f"Weights file not found at {weights_path}")
        except Exception as e:
            logger.error(f"Failed to load weights: {str(e)}")
            raise
