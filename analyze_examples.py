"""
Aesthetic Lens - Example Image Analyzer

This utility script automatically analyzes example images using the NIMA model,
assigns scores, and organizes them according to the project's conventions.

Copyright (c) 2025 Nicole LeGuern
Licensed under MIT License with attribution requirements
https://github.com/CodeQueenie/Aesthetic-Lens---AI_Powered_Image_Aesthetic_Scoring_Tool
"""

import os
import json
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import datetime
import sys
import numpy as np

# Import the scoring model and utilities from the main application
sys.path.append('.')
from model.nima_model import NimaModel
from model.utils import preprocess_image

class ExampleAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Example Image Analyzer")
        self.root.geometry("900x700")
        
        # Set up paths
        self.examples_dir = os.path.join("static", "images", "examples")
        self.metadata_file = os.path.join(self.examples_dir, "examples_metadata.json")
        
        # Load the NIMA model
        self.status_var = tk.StringVar(value="Loading NIMA model...")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.root.update()
        try:
            self.model = NimaModel()
            self.status_var.set("NIMA model loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load NIMA model: {str(e)}")
            self.root.quit()
            return
        
        # Load existing metadata if available
        self.metadata = {}
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r") as f:
                    self.metadata = json.load(f)
            except json.JSONDecodeError:
                self.metadata = {}
        
        # Get list of image files
        self.image_files = self.get_image_files()
        self.current_index = 0
        
        # Set up the UI
        self.setup_ui()
        
        # Load the first image if available
        if self.image_files:
            self.load_current_image()
        else:
            messagebox.showinfo("No Images", "No images found in the examples directory.")
    
    def get_image_files(self):
        """Get list of image files in the examples directory."""
        if not os.path.exists(self.examples_dir):
            os.makedirs(self.examples_dir)
            return []
        
        return [f for f in os.listdir(self.examples_dir) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png')) 
                and not f.startswith(('low_score_', 'average_score_', 'high_score_', 'excellent_score_'))]
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Image display area
        self.image_label = ttk.Label(main_frame)
        self.image_label.pack(pady=10)
        
        # File info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="Current File:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.file_label = ttk.Label(info_frame, text="")
        self.file_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(info_frame, text=f"File {self.current_index + 1} of {len(self.image_files)}").grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5)
        
        # Score display
        score_frame = ttk.Frame(main_frame)
        score_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(score_frame, text="Analyzed Score:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.score_label = ttk.Label(score_frame, text="", font=("Arial", 14, "bold"))
        self.score_label.grid(row=0, column=1, padx=5)
        
        ttk.Label(score_frame, text="Category:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.category_label = ttk.Label(score_frame, text="", font=("Arial", 14, "bold"))
        self.category_label.grid(row=0, column=3, padx=5)
        
        # Manual override
        override_frame = ttk.LabelFrame(main_frame, text="Manual Override (Optional)")
        override_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(override_frame, text="Score (1-10):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.override_score_var = tk.DoubleVar(value=0.0)
        score_scale = ttk.Scale(override_frame, from_=1.0, to=10.0, variable=self.override_score_var, orient=tk.HORIZONTAL, length=300)
        score_scale.grid(row=0, column=1, padx=5, pady=5)
        
        self.override_score_label = ttk.Label(override_frame, text="Not Set")
        self.override_score_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Update override score label when slider changes
        self.override_score_var.trace_add("write", self.update_override_score_label)
        
        ttk.Button(override_frame, text="Apply Override", command=self.apply_override).grid(row=0, column=3, padx=5, pady=5)
        
        # Description
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(desc_frame, text="Description:").grid(row=0, column=0, sticky=tk.NW, padx=5)
        self.description_text = tk.Text(desc_frame, height=3, width=60)
        self.description_text.grid(row=0, column=1, padx=5)
        
        # Contributor
        contrib_frame = ttk.Frame(main_frame)
        contrib_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(contrib_frame, text="Contributor:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.contributor_var = tk.StringVar(value="Admin")
        ttk.Entry(contrib_frame, textvariable=self.contributor_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Previous", command=self.previous_image).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Next", command=self.next_image).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Save and Next", command=self.save_and_next).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Save All Remaining", command=self.save_all_remaining).grid(row=0, column=3, padx=5)
    
    def update_override_score_label(self, *args):
        """Update the override score label when the slider changes."""
        self.override_score_label.config(text=f"{self.override_score_var.get():.1f}")
    
    def apply_override(self):
        """Apply the manual score override."""
        self.score = round(self.override_score_var.get(), 1)
        self.update_score_display()
    
    def get_category_from_score(self, score):
        """Determine the category based on the score."""
        if score <= 3.0:
            return "low"
        elif score <= 6.0:
            return "average"
        elif score <= 8.0:
            return "high"
        else:
            return "excellent"
    
    def update_score_display(self):
        """Update the score and category display."""
        self.score_label.config(text=f"{self.score:.1f}")
        self.category = self.get_category_from_score(self.score)
        self.category_label.config(text=self.category.capitalize())
    
    def load_current_image(self):
        """Load and display the current image."""
        if not self.image_files:
            return
        
        if self.current_index < 0:
            self.current_index = 0
        elif self.current_index >= len(self.image_files):
            self.current_index = len(self.image_files) - 1
        
        filename = self.image_files[self.current_index]
        file_path = os.path.join(self.examples_dir, filename)
        
        # Update file info
        self.file_label.config(text=filename)
        
        # Load and resize image
        try:
            img = Image.open(file_path)
            
            # Calculate new dimensions to fit in the window
            max_width = 800
            max_height = 400
            img_width, img_height = img.size
            
            # Calculate scaling factor
            scale = min(max_width / img_width, max_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage and display
            photo = ImageTk.PhotoImage(img_resized)
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference
            
            # Analyze the image
            self.status_var.set(f"Analyzing image {self.current_index + 1} of {len(self.image_files)}: {filename}")
            self.root.update()
            
            # Use the NIMA model to get the score
            try:
                # Preprocess the image for the model
                preprocessed_image = preprocess_image(file_path)
                
                # Get the predicted score
                self.score = self.model.predict(preprocessed_image)
                self.update_score_display()
                
                # Update status
                self.status_var.set(f"Viewing image {self.current_index + 1} of {len(self.image_files)}: {filename} (Score: {self.score:.1f})")
            except Exception as e:
                self.status_var.set(f"Error analyzing image: {str(e)}")
                messagebox.showerror("Analysis Error", f"Failed to analyze image: {str(e)}")
                self.score = 5.0  # Default score
                self.update_score_display()
            
        except Exception as e:
            self.status_var.set(f"Error loading image: {str(e)}")
    
    def previous_image(self):
        """Go to the previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()
            self.clear_form()
    
    def next_image(self):
        """Go to the next image without saving."""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_current_image()
            self.clear_form()
    
    def clear_form(self):
        """Clear the form fields."""
        self.override_score_var.set(0.0)
        self.override_score_label.config(text="Not Set")
        self.description_text.delete("1.0", tk.END)
        self.contributor_var.set("Admin")
    
    def save_current_image(self):
        """Save metadata for the current image and rename it."""
        if not self.image_files:
            return False
        
        try:
            # Get form data
            category = self.category
            description = self.description_text.get("1.0", tk.END).strip()
            contributor = self.contributor_var.get()
            
            # Get current filename
            old_filename = self.image_files[self.current_index]
            old_path = os.path.join(self.examples_dir, old_filename)
            
            # Count existing examples in this category
            existing_files = [f for f in os.listdir(self.examples_dir) 
                             if f.startswith(f"{category}_score_") and f.endswith((".jpg", ".jpeg", ".png"))]
            next_number = len(existing_files) + 1
            
            # Create new filename
            file_ext = os.path.splitext(old_filename)[1].lower()
            new_filename = f"{category}_score_{next_number}{file_ext}"
            new_path = os.path.join(self.examples_dir, new_filename)
            
            # Rename the file
            shutil.copy2(old_path, new_path)
            
            # Add metadata
            self.metadata[new_filename] = {
                "score": self.score,
                "contributor": contributor,
                "description": description,
                "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save metadata
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=4)
            
            # Update status
            self.status_var.set(f"Saved {old_filename} as {new_filename}")
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving image: {str(e)}")
            return False
    
    def save_and_next(self):
        """Save the current image and go to the next one."""
        if self.save_current_image():
            # Remove the current file from the list
            old_filename = self.image_files.pop(self.current_index)
            
            # Delete the original file
            old_path = os.path.join(self.examples_dir, old_filename)
            try:
                os.remove(old_path)
            except Exception as e:
                print(f"Warning: Could not delete original file {old_path}: {str(e)}")
            
            # If there are more images, load the next one (which is now at the same index)
            if self.image_files:
                self.load_current_image()
                self.clear_form()
            else:
                messagebox.showinfo("Complete", "All images have been processed!")
                self.root.quit()
    
    def save_all_remaining(self):
        """Save all remaining images with current settings."""
        if not self.image_files:
            return
        
        # Get form data for all remaining images
        description = self.description_text.get("1.0", tk.END).strip()
        contributor = self.contributor_var.get()
        
        # Process each remaining image
        processed = 0
        while self.current_index < len(self.image_files):
            # Analyze the current image
            filename = self.image_files[self.current_index]
            file_path = os.path.join(self.examples_dir, filename)
            
            try:
                # Update status
                self.status_var.set(f"Analyzing image {processed+1} of {len(self.image_files)}: {filename}")
                self.root.update()
                
                # Use the NIMA model to get the score
                preprocessed_image = preprocess_image(file_path)
                score = self.model.predict(preprocessed_image)
                category = self.get_category_from_score(score)
                
                # Count existing examples in this category
                existing_files = [f for f in os.listdir(self.examples_dir) 
                                 if f.startswith(f"{category}_score_") and f.endswith((".jpg", ".jpeg", ".png"))]
                next_number = len(existing_files) + 1
                
                # Create new filename
                file_ext = os.path.splitext(filename)[1].lower()
                new_filename = f"{category}_score_{next_number}{file_ext}"
                new_path = os.path.join(self.examples_dir, new_filename)
                
                # Rename the file
                shutil.copy2(file_path, new_path)
                
                # Add metadata
                self.metadata[new_filename] = {
                    "score": score,
                    "contributor": contributor,
                    "description": description,
                    "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Delete the original file
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Warning: Could not delete original file {file_path}: {str(e)}")
                
                # Remove from list and increment counter
                self.image_files.pop(self.current_index)
                processed += 1
                
            except Exception as e:
                messagebox.showerror("Error", f"Error processing image {filename}: {str(e)}")
                self.current_index += 1
        
        # Save metadata
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=4)
        
        messagebox.showinfo("Complete", f"Processed {processed} images!")
        self.root.quit()

def main():
    root = tk.Tk()
    app = ExampleAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
