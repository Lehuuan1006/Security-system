import sys
import os
import cv2
import pandas as pd
import face_recognition
import numpy as np
import time
import serial
import requests
import yagmail
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QFormLayout, QLineEdit, QDateEdit, QComboBox, QListWidget,
    QMessageBox
)
from PyQt5.QtCore import QDate, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from ultralytics import YOLO


# Tải mô hình YOLOv5 (sử dụng model pre-trained)
model = YOLO('yolov5s.pt')


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cap = None  # VideoCapture object
        self.is_camera_open = False  # Flag to track camera status
        self.encodelistknown = []
        self.classNames = []
        self.load_known_faces()  # Load known face encodings
        self.last_capture_time = time.time()
        self.capture_interval = 5  # Seconds
        self.serial_port = None  # Serial port object

        self.setup_serial_port()  # Setup the serial port


    def initUI(self):
        self.setWindowTitle("Face Recognition System")
        self.setGeometry(100, 100, 800, 600)
        
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        self.tab_login = QWidget()
        self.tab_home = QWidget()
        self.tab_signup = QWidget()
        self.tab_info = QWidget()
        
        self.tabs.addTab(self.tab_login, "Login")
        self.tabs.addTab(self.tab_home, "Home")
        self.tabs.addTab(self.tab_signup, "Sign Up")
        self.tabs.addTab(self.tab_info, "Information")
        
        self.loginUI()
        self.homeUI()
        self.signupUI()
        self.infoUI()
        
        self.tabs.setTabEnabled(1, False)  # Disable "Home" tab initially
        self.tabs.setTabEnabled(2, False)  # Disable "Sign Up" tab initially
        self.tabs.setTabEnabled(3, False)  # Disable "Information" tab initially
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def loginUI(self):
        layout = QVBoxLayout()
        
        self.login_label = QLabel("Camera Feed", self)
        self.login_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.login_label)
        
        self.start_login_button = QPushButton("Start Camera", self)
        self.start_login_button.clicked.connect(self.start_login_camera)
        
        self.login_status = QLabel("", self)
        self.login_status.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.start_login_button)
        layout.addWidget(self.login_status)
        
        self.tab_login.setLayout(layout)
    
    def start_login_camera(self):
        if not self.is_camera_open:
            self.cap = cv2.VideoCapture(0)  # Mở camera của laptop (index 0)
            self.is_camera_open = True
            self.start_login_button.setText("Stop Camera")

            # Bắt đầu thread để lấy dữ liệu từ camera
            self.display_login_camera()
        else:
            self.cap.release()
            self.is_camera_open = False
            self.start_login_button.setText("Start Camera")
            self.login_label.clear()
            self.login_status.setText("")
    
    def display_login_camera(self):
        if self.is_camera_open:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Horizontal flip
                frame_rgb = cv2.flip(frame_rgb, 1)
                
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.login_label.setPixmap(QPixmap.fromImage(qt_image))

                face_locations = face_recognition.face_locations(frame_rgb)
                face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
                
                if face_encodings:
                    matches = face_recognition.compare_faces(self.encodelistknown, face_encodings[0])
                    face_distances = face_recognition.face_distance(self.encodelistknown, face_encodings[0])
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                        name = self.classNames[best_match_index]
                        self.login_status.setText(f"Login Success: {name}")
                        self.tabs.setTabEnabled(1, True)  # Enable "Home" tab
                        self.tabs.setTabEnabled(2, True)  # Enable "Sign Up" tab
                        self.tabs.setTabEnabled(3, True)  # Enable "Information" tab
                    else:
                        self.login_status.setText("Login Failed: Unknown User")
                        self.tabs.setTabEnabled(1, False)  # Disable "Home" tab
                        self.tabs.setTabEnabled(2, False)  # Disable "Sign Up" tab
                        self.tabs.setTabEnabled(3, False)  # Disable "Information" tab
                else:
                    self.login_status.setText("No face detected")

            QTimer.singleShot(30, self.display_login_camera)

    def homeUI(self):
        layout = QVBoxLayout()
        
        self.camera_label = QLabel("Camera Feed", self)
        self.camera_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.camera_label)
        
        self.start_button = QPushButton("Start Camera", self)
        self.start_button.clicked.connect(self.start_home_camera)
        layout.addWidget(self.start_button)
        
        control_layout = QHBoxLayout()
        self.up_button = QPushButton("Up", self)
        self.down_button = QPushButton("Down", self)
        self.right_button = QPushButton("Right", self)
        self.left_button = QPushButton("Left", self)

        self.down_button.clicked.connect(lambda: self.send_command('1'))#---------------------------------------------
        self.up_button.clicked.connect(lambda: self.send_command('2'))#---------------------------------------------
        self.right_button.clicked.connect(lambda: self.send_command('3'))#---------------------------------------------
        self.left_button.clicked.connect(lambda: self.send_command('4'))#---------------------------------------------

        
        control_layout.addWidget(self.up_button)
        control_layout.addWidget(self.down_button)
        control_layout.addWidget(self.right_button)
        control_layout.addWidget(self.left_button)
        
        layout.addLayout(control_layout)
        self.tab_home.setLayout(layout)

    def send_command(self, command):#---------------------------------------------
        """Send a command to the Arduino via serial."""#---------------------------------------------
        if self.serial_port.is_open:#---------------------------------------------
            self.serial_port.write(command.encode())#---------------------------------------------
        else:#---------------------------------------------
            print("Serial port is not open")#---------------------------------------------

    def setup_serial_port(self):
        try:
            self.serial_port = serial.Serial(
                port='COM5',  # Update this to your actual port
                baudrate=9600,
                timeout=1
            )
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")

    def start_home_camera(self):
        if not hasattr(self, 'is_camera_open') or not self.is_camera_open:
            url = "http://192.168.1.149:81/stream"  # Change this URL if ESP32-CAM IP is different
            self.cap = cv2.VideoCapture(url)

            if self.cap.isOpened():
                self.is_camera_open = True
                self.start_button.setText("Stop Camera")

                # Start a thread to retrieve data from the camera
                self.display_home_camera()
            else:
                QMessageBox.warning(self, "Camera Error", "Failed to open camera stream.")
        else:
            self.cap.release()
            self.is_camera_open = False
            self.start_button.setText("Start Camera")
            self.camera_label.clear()

    def display_home_camera(self):
        if hasattr(self, 'is_camera_open') and self.is_camera_open:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Perform YOLO detection
                results = model(frame_rgb)
                
                # Filter out people detections (assuming '0' is the class index for people)
                detected_people = [r for r in results[0].boxes if r.cls[0] == 0]
                
                if len(detected_people) > 0:
                    for person in detected_people:
                        box = person.xyxy[0].cpu().numpy().astype(int)
                        x_min, y_min, x_max, y_max = box  # Extract coordinates
                        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.putText(frame, 'Person detected', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    
                    # Capture image when a person is detected
                    current_time = time.time()
                    timestamp = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(current_time))
                    date = time.strftime('%Y-%m-%d', time.localtime(current_time))
                    # Create directory for the current date if it doesn't exist
                    date_dir = os.path.join('C:/Users/ADMIN/Downloads/doan1/App/person_detected', date)
                    os.makedirs(date_dir, exist_ok=True)
                    # Save the captured image (use original BGR frame)
                    image_path = os.path.join(date_dir, f'{timestamp}.jpg')
                    cv2.imwrite(image_path, frame)
                else:
                    # Display "Secure" status
                    cv2.putText(frame, 'Secure', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                
                # Convert frame to QImage and display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.camera_label.setPixmap(QPixmap.fromImage(qt_image))
                
            QTimer.singleShot(30, self.display_home_camera)



    def signupUI(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate())
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Date of Birth:", self.dob_input)
        form_layout.addRow("Gender:", self.gender_input)
        
        self.camera_signup_label = QLabel("Camera Feed", self)
        self.camera_signup_label.setAlignment(Qt.AlignCenter)
        
        self.start_signup_button = QPushButton("Start Camera", self)
        self.start_signup_button.clicked.connect(self.start_camera)
        
        self.capture_button = QPushButton("Capture Photo", self)
        self.capture_button.setEnabled(False)
        self.capture_button.clicked.connect(self.capture_photo)
        
        self.save_button = QPushButton("Save Information", self)
        self.save_button.clicked.connect(self.save_information)
        
        layout.addLayout(form_layout)
        layout.addWidget(self.camera_signup_label)
        layout.addWidget(self.start_signup_button)
        layout.addWidget(self.capture_button)
        layout.addWidget(self.save_button)
        
        self.tab_signup.setLayout(layout)
    
    def infoUI(self):
        layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter keyword to search...")
        self.search_input.textChanged.connect(self.filter_information)
        
        self.info_list = QListWidget()
        self.info_list.setSelectionMode(QListWidget.SingleSelection)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_information)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_information)
        
        layout.addWidget(self.search_input)
        layout.addWidget(self.info_list)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        
        self.tab_info.setLayout(layout)

    def load_known_faces(self):
        path = 'C:/Users/ADMIN/Downloads/doan1/App/photos'
        if not os.path.exists(path):
            os.makedirs(path)
        
        images = []
        self.classNames = []
        mylist = os.listdir(path)
        for cl in mylist:
            curImg = cv2.imread(f'{path}/{cl}')
            images.append(curImg)
            self.classNames.append(os.path.splitext(cl)[0])
        
        self.encodelistknown = self.find_encodings(images)

    def find_encodings(self, images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encodes = face_recognition.face_encodings(img)
            if encodes:
                encodeList.append(encodes[0])
        return encodeList

    def start_camera(self):
        if not hasattr(self, 'is_camera_open') or not self.is_camera_open:
            self.cap = cv2.VideoCapture(0)  # Open laptop camera (index 0)
            self.is_camera_open = True
            self.start_signup_button.setText("Stop Camera")
            self.capture_button.setEnabled(True)  # Enable Capture Photo button

            # Start a thread to retrieve data from the camera
            self.display_camera()
        else:
            self.cap.release()
            self.is_camera_open = False
            self.start_signup_button.setText("Start Camera")
            self.capture_button.setEnabled(False)  # Disable Capture Photo button
            self.camera_signup_label.clear()

    def display_camera(self):
        if hasattr(self, 'is_camera_open') and self.is_camera_open:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Horizontal flip
                frame_rgb = cv2.flip(frame_rgb, 1)
                
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.camera_signup_label.setPixmap(QPixmap.fromImage(qt_image))
            QTimer.singleShot(30, self.display_camera)

    def capture_photo(self):
        if hasattr(self, 'is_camera_open') and self.is_camera_open and self.name_input.text().strip():
            ret, frame = self.cap.read()
            if ret:
                name = self.name_input.text().strip()
                image_path = f"C:/Users/ADMIN/Downloads/doan1/App/photos/{name}.jpg"
                cv2.imwrite(image_path, frame)
                self.process_and_save_face_encoding(frame, name)
                self.load_known_faces()  # Update known faces
                QMessageBox.information(self, "Capture", f"Photo captured and saved as {image_path}.")
        else:
            QMessageBox.warning(self, "Capture Error", "Camera is not open or Name is not provided.")

    def process_and_save_face_encoding(self, image, name):
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(image_rgb)
            if face_encodings:
                encoding_path = f"C:/Users/ADMIN/Downloads/doan1/App/encodings/{name}.npy"
                np.save(encoding_path, face_encodings[0])
                QMessageBox.information(self, "Encoding", f"Face encoding saved as {encoding_path}.")
            else:
                QMessageBox.warning(self, "Encoding Error", "No face detected in the captured photo.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not process face encoding: {e}")

    def save_information(self):
        name = self.name_input.text().strip()
        dob = self.dob_input.date().toString("yyyy-MM-dd")
        gender = self.gender_input.currentText()
        
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a name.")
            return
        
        csv_file = "C:/Users/ADMIN/Downloads/doan1/App/signups.csv"
        
        try:
            df = pd.read_csv(csv_file) if pd.io.common.file_exists(csv_file) else pd.DataFrame(columns=["Name", "Date of Birth", "Gender"])
            
            if name in df["Name"].values:
                df.loc[df["Name"] == name, ["Date of Birth", "Gender"]] = [dob, gender]
            else:
                new_entry = pd.DataFrame([{"Name": name, "Date of Birth": dob, "Gender": gender}])
                df = pd.concat([df, new_entry], ignore_index=True)
                
            df.to_csv(csv_file, index=False)
            QMessageBox.information(self, "Success", "Information saved successfully.")
            
            self.name_input.clear()
            self.dob_input.setDate(QDate.currentDate())
            self.gender_input.setCurrentIndex(0)
            
            self.load_information()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save information: {e}")

    def load_information(self):
        self.search_input.setText("")  # Clear keyword to load all information
        self.filter_information()

    def filter_information(self):
        keyword = self.search_input.text().lower()
        csv_file = "C:/Users/ADMIN/Downloads/doan1/App/signups.csv"
        
        try:
            if pd.io.common.file_exists(csv_file):
                df = pd.read_csv(csv_file)
                self.info_list.clear()
                for _, row in df.iterrows():
                    info = f"Name: {row['Name']}, Date of Birth: {row['Date of Birth']}, Gender: {row['Gender']}"
                    if keyword in info.lower():
                        self.info_list.addItem(info)
            else:
                self.info_list.clear()
                self.info_list.addItem("No data available.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load information: {e}")

    def edit_information(self):
        selected_items = self.info_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an item to edit.")
            return
        
        selected_item = selected_items[0].text()
        details = selected_item.split(", ")
        name = details[0].split(": ")[1]
        dob = details[1].split(": ")[1]
        gender = details[2].split(": ")[1]

        # Populate Sign Up tab for editing
        self.tabs.setCurrentIndex(2)
        self.name_input.setText(name)
        self.dob_input.setDate(QDate.fromString(dob, "yyyy-MM-dd"))
        self.gender_input.setCurrentText(gender)

    def delete_information(self):
        selected_items = self.info_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an item to delete.")
            return
        
        selected_item = selected_items[0].text()
        details = selected_item.split(", ")
        name = details[0].split(": ")[1]
        
        csv_file = "C:/Users/ADMIN/Downloads/doan1/App/signups.csv"
        try:
            if pd.io.common.file_exists(csv_file):
                df = pd.read_csv(csv_file)
                df = df[df["Name"] != name]  # Remove selected information
                df.to_csv(csv_file, index=False)
                self.load_information()
                QMessageBox.information(self, "Success", "Information deleted successfully.")
            else:
                QMessageBox.warning(self, "No Data", "No data available to delete.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not delete information: {e}")

    def on_tab_changed(self, index):
        if index == 3:  # Tab "Information" has index 3
            self.load_information()
        if index == 0:  # Tab "Home" has index 0
            if hasattr(self, 'is_camera_open') and self.is_camera_open:
                # Stop displaying camera feed when switching away from Home tab
                self.cap.release()
                self.is_camera_open = False
                self.start_button.setText("Start Camera")
                self.camera_label.clear()

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
