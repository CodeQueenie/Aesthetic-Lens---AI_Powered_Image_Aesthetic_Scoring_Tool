# Aesthetic Lens - AI-Powered Image Aesthetic Scoring Tool

Aesthetic Lens is an AI-powered tool that evaluates the aesthetic quality of images using a pre-trained NIMA (Neural Image Assessment) model. This application provides a sophisticated web interface for users to upload images and receive detailed aesthetic analysis.

## Features

- Upload images through a modern, intuitive web interface
- Process images using a pre-trained NIMA model based on MobileNet architecture
- Receive an aesthetic score (1-10) with detailed visual feedback
- View example images with their scores for reference and comparison
- Contribute to the example gallery with your own images
- Administrative interface for managing example images
- Utility scripts for batch processing and organizing images

## Understanding Aesthetic Scores

The NIMA model evaluates images on a scale from 1 to 10, with higher scores indicating better aesthetic quality:

- **1-3**: Images with significant technical issues (poor lighting, composition, focus)
- **4-6**: Average images with decent technical quality but lacking artistic elements
- **7-8**: Good quality images with strong composition and technical execution
- **9-10**: Exceptional images with professional quality, typically featuring:
  - Perfect composition following photography principles (rule of thirds, leading lines)
  - Optimal lighting conditions with balanced exposure
  - Rich, harmonious color palettes or masterful black and white treatment
  - Clear subject focus with pleasing depth of field
  - Emotional impact or storytelling elements
  - Professional post-processing without appearing over-edited

Note that the model was trained on professional photography datasets, so it tends to favor images that follow established photography principles and may score artistic or unconventional images lower than a human might.

## Tech Stack

- **Backend**: Flask (Python)
- **AI Model**: TensorFlow implementation of NIMA with MobileNet
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Environment Management**: Conda
- **Image Processing**: PIL, NumPy, TensorFlow

## Project Structure

```
aesthetic-lens/
├── app.py                  # Main Flask application
├── model/                  # Model-related files
│   ├── __init__.py
│   ├── nima_model.py       # NIMA model implementation
│   └── utils.py            # Utility functions for image processing
├── static/                 # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
├── templates/              # HTML templates
│   ├── index.html          # Home page with upload form
│   ├── result.html         # Results display page
│   ├── examples.html       # Example gallery page
│   └── admin_examples.html # Admin interface for examples
├── uploads/                # Storage for uploaded images
├── examples/               # Storage for example images
├── analyze_examples.py     # Utility for analyzing and organizing example images
├── organize_examples.py    # Utility for manually organizing example images
├── requirements.txt        # Python dependencies
├── environment.yml         # Conda environment specification
└── README.md               # Project documentation
```

## Installation

### Using Conda (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/CodeQueenie/Aesthetic-Lens---AI_Powered_Image_Aesthetic_Scoring_Tool.git
   cd Aesthetic-Lens---AI_Powered_Image_Aesthetic_Scoring_Tool
   ```

2. Create and activate a Conda environment:
   ```
   conda env create -f environment.yml
   conda activate aesthetic-lens
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

### Web Interface

1. Access the web interface at `http://localhost:5000`
2. Click on the "Upload Image" button to select an image from your computer
3. The application will process the image and display an aesthetic score
4. Review the score and feedback to understand the aesthetic quality of your image
5. Navigate to the "Examples" page to view reference images with their scores

### Admin Interface

1. Access the admin interface at `http://localhost:5000/admin/examples`
2. View, edit, and delete example images
3. Add new example images with scores and descriptions

### Utility Scripts

#### Analyze Examples

The `analyze_examples.py` script uses the NIMA model to automatically score and organize example images:

```
python analyze_examples.py
```

#### Organize Examples

The `organize_examples.py` script provides a GUI for manually scoring and organizing example images:

```
python organize_examples.py
```

## Deployment

### Local Deployment

Follow the installation instructions above to run the application locally.

### Cloud Deployment Options

See the `DEPLOYMENT.md` file for detailed instructions on deploying to various cloud platforms.

## License

MIT

Copyright (c) 2025 Nicole LeGuern

### Attribution Requirements
When using or adapting this code, please include the following attribution:
"Aesthetic Lens - AI-Powered Image Aesthetic Scoring Tool by Nicole LeGuern (https://github.com/CodeQueenie/Aesthetic-Lens---AI_Powered_Image_Aesthetic_Scoring_Tool)"

## Acknowledgments

- The NIMA model is based on the research paper: ["NIMA: Neural Image Assessment"](https://arxiv.org/abs/1709.05424) by Hossein Talebi and Peyman Milanfar.
- MobileNet architecture provided by Google via TensorFlow Hub.
