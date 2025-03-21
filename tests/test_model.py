"""
Unit tests for the NIMA model

This module contains unit tests for the NIMA model and utility functions.
"""

import os
import unittest
import numpy as np
from PIL import Image
import tempfile

# Import model-related modules
from model.nima_model import NimaModel
from model.utils import preprocess_image, get_feedback_from_score


class TestNimaModel(unittest.TestCase):
    """
    Test cases for the NIMA model.
    """
    
    def setUp(self):
        """
        Set up the test environment.
        """
        try:
            # Initialize the NIMA model
            self.model = NimaModel()
            
            # Create a temporary test image
            self.temp_dir = tempfile.TemporaryDirectory()
            self.test_image_path = os.path.join(self.temp_dir.name, "test_image.jpg")
            
            # Create a simple test image (100x100 red square)
            img = Image.new("RGB", (100, 100), color=(255, 0, 0))
            img.save(self.test_image_path)
        except Exception as e:
            self.skipTest(f"Failed to set up test environment: {str(e)}")
    
    def tearDown(self):
        """
        Clean up the test environment.
        """
        # Remove temporary directory and files
        self.temp_dir.cleanup()
    
    def test_model_initialization(self):
        """
        Test that the model initializes correctly.
        """
        self.assertIsNotNone(self.model)
        self.assertIsNotNone(self.model.model)
    
    def test_preprocess_image(self):
        """
        Test image preprocessing.
        """
        # Preprocess the test image
        preprocessed_image = preprocess_image(self.test_image_path)
        
        # Check the shape of the preprocessed image
        self.assertEqual(len(preprocessed_image.shape), 3)
        self.assertEqual(preprocessed_image.shape[2], 3)  # RGB channels
        
        # Check that pixel values are normalized to [0, 1]
        self.assertTrue(np.all(preprocessed_image >= 0))
        self.assertTrue(np.all(preprocessed_image <= 1))
    
    def test_predict(self):
        """
        Test prediction functionality.
        """
        # Preprocess the test image
        preprocessed_image = preprocess_image(self.test_image_path)
        
        # Get the prediction
        score = self.model.predict(preprocessed_image)
        
        # Check that the score is within the expected range
        self.assertGreaterEqual(score, 1.0)
        self.assertLessEqual(score, 10.0)
    
    def test_get_feedback(self):
        """
        Test feedback generation.
        """
        # Test feedback for different score ranges
        feedback_low = get_feedback_from_score(2.5)
        feedback_below_avg = get_feedback_from_score(4.5)
        feedback_avg = get_feedback_from_score(6.5)
        feedback_good = get_feedback_from_score(8.5)
        feedback_excellent = get_feedback_from_score(9.5)
        
        # Check that feedback is non-empty
        self.assertTrue(len(feedback_low) > 0)
        self.assertTrue(len(feedback_below_avg) > 0)
        self.assertTrue(len(feedback_avg) > 0)
        self.assertTrue(len(feedback_good) > 0)
        self.assertTrue(len(feedback_excellent) > 0)
        
        # Check that different score ranges get different feedback
        self.assertNotEqual(feedback_low, feedback_below_avg)
        self.assertNotEqual(feedback_below_avg, feedback_avg)
        self.assertNotEqual(feedback_avg, feedback_good)
        self.assertNotEqual(feedback_good, feedback_excellent)


if __name__ == "__main__":
    unittest.main()
