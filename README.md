# Face Detection API

## Project Overview
This is a Flask-based Face Detection API that provides facial recognition capabilities. The API allows you to:
- Add new faces to the recognition database
- Recognize faces from provided images

## Prerequisites
- Python 3.12.x
- Ability to create Python virtual environments
- Windows, Linux, or macOS operating system

## Installation Instructions

### 1. Create and Activate Virtual Environment

On Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.ps1
```

On Linux/macOS:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 2. Install Dependencies
With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

The project depends on the following packages:
- flask
- setuptools
- numpy
- opencv-python
- face_recognition
- face_recognition_models

Note: The `face_recognition` package requires `dlib` which might need additional system dependencies. If you encounter installation issues, please ensure you have the appropriate C++ build tools installed on your system.

## Project Setup

### 1. Create Known Faces Directory
The application requires a directory to store known faces. The directory will be automatically created when the application runs, but you can create it manually:

```bash
mkdir known_faces
```

### 2. Directory Structure
Organize your known faces in the following structure:
```
known_faces/
    person1_name/
        image1.jpg
        image2.jpg
    person2_name/
        image1.jpg
        ...
```

## Running the Application

1. Ensure your virtual environment is activated
2. Run the Flask application:
```bash
python main.py
```

The server will start on `http://0.0.0.0:5000` in debug mode.

## API Endpoints

### 1. Add Person
- **Endpoint**: `/add_person`
- **Method**: POST
- **Payload**:
  ```json
  {
    "name": "person_name",
    "image": "base64_encoded_image"
  }
  ```
- **Description**: Adds a new person to the recognition database. The image should be base64 encoded and contain a single face.

### 2. Recognize Face
- **Endpoint**: `/recognize`
- **Method**: POST
- **Payload**:
  ```json
  {
    "image": "base64_encoded_image"
  }
  ```
- **Description**: Recognizes a face in the provided image. The image should contain a single face. Returns the person's name and confidence score if recognized.

## Development Notes
- The application runs in debug mode by default
- Images are stored in the `known_faces` directory
- Only one face per image is supported for both adding and recognizing faces

