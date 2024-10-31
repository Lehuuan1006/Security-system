# **Human Motion Detection and Security Alert System**
This project implements a human motion detection, face data verification, and security alert system using machine vision and IoT technologies. It leverages the ESP32-CAM for real-time monitoring and integrates YOLOv5 for object detection and OpenCV for face recognition, creating a secure and efficient surveillance solution.

## **Project Overview**
With the rise in security concerns, the need for smart surveillance solutions has grown. This system was designed to detect human motion, identify faces from a pre-registered database, and issue alerts to designated users. Key features include real-time streaming, face authentication, motion tracking, and a user-friendly interface for system control. Link System demo: https://drive.google.com/drive/folders/1Xu5WDIanh8UqaNph10PIVM5tNPEqGjRM?usp=sharing

## **Features**
- Real-time Human Motion Detection: Utilizes YOLOv5 to detect human presence and capture motion in various environments.
- Face Recognition: OpenCV and face_recognition libraries are used to verify registered faces during system access.
- Remote Camera Control: ESP32-CAM is mounted with a servo system to adjust the viewing angle, enabling flexible monitoring.
- User Management: Allows administrators to add, update, or delete users, ensuring the system remains secure and up-to-date.
## **Technologies**
- Hardware: ESP32-CAM, Arduino Nano, Servo SG90
- Software: PyQt5 for interface, OpenCV, face_recognition, and YOLOv5 for object detection
- Programming Languages: Python (mainly), Arduino IDE for microcontroller programming
## **Usage**
1. Setup: Connect ESP32-CAM to the network and launch the Python application.
2. User Registration: Register users by capturing and encoding their facial data for future authentication.
3. Monitoring: Start live streaming for motion detection; the system triggers alerts and records images upon detecting human presence.
4. Manage Users: Access the control panel to view, update, or remove registered users.
## **Future Development**
Planned improvements include:
- Mobile app integration for remote monitoring
- Enhanced real-time notifications through email or app alerts
- Additional camera support for larger coverage areas
