# EduManager - School Management System

A comprehensive school management system built with Django, featuring attendance tracking, course management, and reporting capabilities. The system includes advanced facial recognition for automated attendance tracking.

## Features

- Course Management
- Attendance Tracking with Facial Recognition
- Student & Staff Management
- Report Generation
- Real-time Attendance Updates

## Face Recognition System

EduManager uses state-of-the-art facial recognition technology to automate attendance tracking:

### Technologies Used
- **OpenCV**: For real-time face detection and image processing
- **Deepface**: For facial recognition and verification
- **TensorFlow**: Backend for deep learning models (used by Deepface)

### Requirements for Face Recognition

Before installing the main project, ensure you have the following dependencies for face recognition:

#### Windows
```powershell
# Install Visual C++ Build Tools (required for dlib)
# Download and install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

#### Linux
```bash
# Install required system libraries
sudo apt-get update
sudo apt-get install python3-opencv
sudo apt-get install libopencv-dev
sudo apt-get install cmake
sudo apt-get install libx11-dev
sudo apt-get install libatlas-base-dev
```

### Additional Python Dependencies
These will be installed automatically through requirements.txt:
```
deepface==0.0.79
opencv-python==4.7.0.72
tensorflow==2.12.0
```

### Face Recognition Setup Notes

1. **Camera Access**
   - Ensure your system has a working webcam
   - Grant camera permissions to the application
   - For Linux systems, you might need to configure video device permissions:
     ```bash
     sudo usermod -a -G video $USER
     ```

2. **Model Downloads**
   - On first run, Deepface will automatically download required models
   - Ensure you have a stable internet connection during first run
   - Models are cached locally for future use

3. **Performance Considerations**
   - Face recognition requires significant CPU/GPU resources
   - Recommended: CPU with 4+ cores or NVIDIA GPU
   - At least 4GB RAM recommended


## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- Git
- Webcam or Camera device
- Sufficient CPU/GPU power for face recognition


## Installation Guide

### Windows Setup

1. **Clone the Repository**
```bash
git clone https://github.com/younoussaBen/edumanager.git
cd edumanager
```

2. **Set PowerShell Execution Policy**
Open PowerShell as Administrator and run:
```powershell
Set-ExecutionPolicy Unrestricted -Scope Process
```

3. **Create Virtual Environment**
```powershell
python -m venv venv
```

4. **Activate Virtual Environment**
```powershell
.\venv\Scripts\activate
```

5. **Install Visual C++ Build Tools**
   - Download and install Visual C++ Build Tools
   - Select "Desktop development with C++" workload
   - Install Windows 10 SDK

6. **Verify OpenCV Installation**
  ```powershell
  python
  >>> import cv2
  >>> cv2.__version__
  ```

7. **Install Dependencies**
```powershell
pip install -r requirements.txt
```

8. **Setup Database**
```powershell
python manage.py migrate
```

9. **Create Superuser (Admin Account)**
```powershell
python manage.py createsuperuser
```

10. **Run Development Server**
```powershell
python manage.py runserver
```

### Linux/macOS Setup

1. **Clone the Repository**
```bash
git clone https://github.com/younoussaBen/edumanager.git
cd edumanager
```

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-opencv
sudo apt-get install libopencv-dev
sudo apt-get install cmake
sudo apt-get install libx11-dev
sudo apt-get install libatlas-base-dev

# Verify installation
python3
>>> import cv2
>>> cv2.__version__
```


2. **Create Virtual Environment**
```bash
python3 -m venv venv
```

3. **Activate Virtual Environment**
```bash
source venv/bin/activate
```

4. **Install Dependencies**
```bash
pip install -r requirements.txt
```

5. **Setup Database**
```bash
python manage.py migrate
```

6. **Create Superuser (Admin Account)**
```bash
python manage.py createsuperuser
```

7. **Run Development Server**
```bash
python manage.py runserver
```

## Development Workflow

1. Always activate your virtual environment before working:
   - Windows: `.\venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`

2. Install new dependencies:
   ```bash
   pip install package_name
   pip freeze > requirements.txt
   ```

3. Create new migrations after model changes:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Run tests:
   ```bash
   python manage.py test
   ```

## Accessing the Application

1. Admin Interface: `http://localhost:8000/admin/`
2. Main Application: `http://localhost:8000/`

## Testing Face Recognition

After installation, you can test the face recognition system:

1. Navigate to the attendance section
2. Click "Take Attendance"
3. Allow camera access when prompted
4. The system will detect and recognize faces in real-time

## Troubleshooting Face Recognition

### Common Issues

1. **Camera Not Detected**
   - Check camera connections
   - Verify camera permissions
   - Try restarting the application

2. **Slow Recognition Speed**
   - Ensure sufficient system resources
   - Close other resource-intensive applications
   - Consider upgrading hardware for better performance

3. **Model Download Issues**
   - Check internet connection
   - Manually download models if automatic download fails
   - Clear and recreate model cache

### Windows
1. **Permission Denied when activating venv**
   - Open PowerShell as Administrator
   - Run: `Set-ExecutionPolicy Unrestricted -Scope Process`
   - Try activating the virtual environment again

2. **Python Command Not Found**
   - Ensure Python is added to your PATH
   - Try using `py` instead of `python`

### Linux
1. **Python3/pip3 Command Not Found**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Permission Denied when installing packages**
   - Don't use sudo with pip while in virtualenv
   - If needed: `sudo chown -R $USER:$USER venv/`

### Performance Optimization

For better face recognition performance:

1. **Hardware Recommendations**
   - CPU: Intel i5/i7 or AMD equivalent (4+ cores)
   - RAM: 8GB minimum (16GB recommended)
   - GPU: NVIDIA GPU with CUDA support (optional but recommended)

2. **Software Optimization**
   - Use appropriate frame resolution
   - Adjust detection frequency
   - Configure recognition threshold


## Production Deployment Notes

1. Set `DEBUG=False` in production
2. Use a proper database (PostgreSQL recommended)
3. Set up proper static files serving
4. Use a production-grade server (Gunicorn/uWSGI)
5. Set up HTTPS
6. Configure proper email backend


## Support

For support create an issue in the repository.
