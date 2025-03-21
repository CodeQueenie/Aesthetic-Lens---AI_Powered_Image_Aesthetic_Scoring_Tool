/**
 * Aesthetic Lens - Main JavaScript
 * 
 * This file handles the interactive elements of the Aesthetic Lens application,
 * including file uploads, drag and drop functionality, and form submissions.
 */

document.addEventListener("DOMContentLoaded", function() {
    // Get DOM elements
    const uploadArea = document.getElementById("upload-area");
    const fileInput = document.getElementById("file-input");
    const uploadForm = document.getElementById("upload-form");
    const submitBtn = document.getElementById("submit-btn");
    const loadingOverlay = document.getElementById("loading-overlay");
    
    // Only proceed if we're on the upload page
    if (uploadArea && fileInput && uploadForm) {
        // Handle click on upload area
        uploadArea.addEventListener("click", function() {
            fileInput.click();
        });
        
        // Handle file selection
        fileInput.addEventListener("change", function() {
            if (fileInput.files.length > 0) {
                const fileName = fileInput.files[0].name;
                
                // Update upload area to show selected file
                uploadArea.innerHTML = `
                    <i class="fas fa-file-image fa-3x mb-3"></i>
                    <p>${fileName}</p>
                `;
                
                // Add selected class for styling
                uploadArea.parentElement.classList.add("file-selected");
                
                // Enable submit button
                submitBtn.disabled = false;
            }
        });
        
        // Handle drag and drop events
        ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Handle drag enter and over
        ["dragenter", "dragover"].forEach(eventName => {
            uploadArea.addEventListener(eventName, function() {
                uploadArea.classList.add("dragover");
            }, false);
        });
        
        // Handle drag leave and drop
        ["dragleave", "drop"].forEach(eventName => {
            uploadArea.addEventListener(eventName, function() {
                uploadArea.classList.remove("dragover");
            }, false);
        });
        
        // Handle file drop
        uploadArea.addEventListener("drop", function(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                
                // Trigger change event
                const event = new Event("change");
                fileInput.dispatchEvent(event);
            }
        }, false);
        
        // Handle form submission
        uploadForm.addEventListener("submit", function(e) {
            // Check if a file has been selected
            if (!fileInput.files || fileInput.files.length === 0) {
                e.preventDefault();
                alert("Please select an image file first.");
                return;
            }
            
            // Show loading overlay
            if (loadingOverlay) {
                loadingOverlay.classList.remove("d-none");
                document.body.style.overflow = "hidden"; // Prevent scrolling while loading
            }
        });
    }
    
    // Handle score visualization if we're on the results page
    const scoreValue = document.querySelector(".score-value");
    if (scoreValue) {
        const score = parseFloat(scoreValue.textContent);
        const progressBar = document.querySelector(".progress-bar");
        
        // Animate the progress bar
        if (progressBar) {
            progressBar.style.width = "0%";
            setTimeout(() => {
                progressBar.style.transition = "width 1s ease-in-out";
                progressBar.style.width = `${score * 10}%`;
            }, 200);
        }
        
        // Set color based on score
        if (score < 4) {
            scoreValue.parentElement.style.backgroundColor = "#dc3545"; // Danger/red
        } else if (score < 7) {
            scoreValue.parentElement.style.backgroundColor = "#ffc107"; // Warning/yellow
        } else {
            scoreValue.parentElement.style.backgroundColor = "#28a745"; // Success/green
        }
    }
});
