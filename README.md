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

Note: The `face_recognition` package requires `dlib` which might need additional system dependencies. If you encounter
installation issues, please ensure you have the appropriate C++ build tools installed on your system.

## Project Setup

### 1. Create a `.env` File

Create a file named `.env` in the root directory of the project. This file will store your database configuration
settings. Use the following template:

```text
SERVER=
DATABASE=
DB_USER=
DB_PASSWORD=
```

## Running the Application

1. Ensure your virtual environment is activated
2. Run the Flask application:

```bash
python main.py
```

The server will start on `http://0.0.0.0:5000` in debug mode.
