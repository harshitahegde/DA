# SafeGoAI - AI-Based Safety Monitoring and Alert System

An AI-powered safety monitoring system built with **Python, Flask, OpenCV, and MediaPipe** that detects the **Signal for Help gesture**, identifies the person using face recognition, determines an approximate location, and sends emergency alerts through **push notifications and email**.

## 🎯 Project Overview

SafeGoAI is designed as a real-time safety monitoring system that can detect when a person silently signals for help using a camera.

The system combines **computer vision, hand gesture recognition, face recognition, geolocation, and automated notifications** to create an emergency alert workflow.

### How It Works

```text
Camera
   ↓
Hand Gesture Detection
   ↓
Signal for Help Detected
   ↓
Face Recognition
   ↓
Identify Person
   ↓
Approximate Location
   ↓
Capture Evidence Frame
   ↓
Send Emergency Alerts
   ├── Push Notification
   └── Email
```

The system is designed to provide a discreet way for a person to signal distress without verbally asking for help.

---

## ✨ Key Features

* 🖐️ **Signal for Help Gesture Detection**
* 👤 **Face Recognition**
* 📍 **Approximate Location Detection**
* 📸 **Automatic Evidence Capture**
* 📱 **Real-Time Push Notifications**
* 📧 **Emergency Email Alerts**
* ⏱️ **Alert Cooldown Mechanism**
* 🔐 **User Registration and Login**
* 👤 **User Profile Management**
* 🗃️ **SQLite Database**
* 📷 **Webcam-Based Real-Time Monitoring**

---

## 🧠 AI & Computer Vision

### Signal for Help Detection

SafeGoAI uses **MediaPipe Hands** to detect hand landmarks from webcam frames.

The application analyzes the detected hand landmarks to determine whether the user is performing the recognized **Signal for Help** gesture.

To reduce accidental triggers, the gesture must remain detected for a sequence of consecutive frames before an emergency alert is generated.

The current implementation requires the gesture to be detected for **45 consecutive frames**.

---

### Face Recognition

The system uses **OpenCV** and face-recognition functionality to identify the person in front of the camera.

Known faces are stored in the:

```text
known_faces/
```

directory.

When a face is detected:

* The face is converted into an encoding.
* The encoding is compared with known faces.
* If a match is found, the corresponding person's name is displayed.
* If no match is found, the person is identified as **Unknown Person**.

This allows the emergency notification to contain the identity of the detected person when available.

---

## 📍 Approximate Geolocation

When a distress gesture is detected, SafeGoAI retrieves an **approximate location based on the system's public IP address**.

The coordinates are then used to generate a Google Maps location link.

The alert can therefore contain information such as:

```text
Person: Harshita
Location: Google Maps link
```

> The location is approximate and depends on IP-based geolocation. It should not be treated as precise GPS tracking.

---

## 🚨 Emergency Alert System

Once a valid Signal for Help gesture is detected, the system automatically generates an emergency alert.

The alert workflow includes:

1. Detect the distress gesture.
2. Identify the person using face recognition.
3. Obtain approximate location information.
4. Capture the current camera frame.
5. Generate a Google Maps location link.
6. Send a push notification.
7. Send an email alert with the captured image.

### Push Notification

SafeGoAI uses **ntfy.sh** to send urgent push notifications.

The notification can contain:

* Person's identity
* Approximate location
* Google Maps link
* Emergency message

### Email Alert

The system can also send an emergency email using **Gmail SMTP**.

The captured camera frame is attached to the email to provide visual information about the detected event.

---

## ⏱️ Alert Cooldown

To prevent repeated notifications from being generated continuously while the gesture remains visible, the application includes an **alert cooldown mechanism**.

The current implementation uses a **5-minute cooldown period** between emergency alerts.

This reduces notification spam while still allowing the system to continue monitoring.

---

## 🌐 Web Application

The project also contains a Flask-based web application for user management.

### User Features

* User registration
* User login
* Logout
* Profile viewing
* Profile updating
* Profile photograph upload

User information is stored in a SQLite database.

The uploaded profile photographs can also be used as known faces for the face-recognition component.

---

## 🗄️ Database

SafeGoAI uses **SQLite** for storing user information.

The database is initialized using:

```text
init_db.py
```

The user database stores information such as:

* Name
* Email
* Phone number
* Password
* Emergency contact
* Address
* Profile photograph

Passwords are stored using password hashing rather than plain-text storage.

---

## 🏗️ Tech Stack

### Programming Language

* **Python**

### Backend

* **Flask**

### Computer Vision & AI

* **OpenCV**
* **MediaPipe**
* Face recognition

### Database

* **SQLite**

### Notifications

* **ntfy.sh**
* **Gmail SMTP**

### Frontend

* **HTML**
* **CSS**
* **JavaScript**

### APIs / Services

* IP-based geolocation
* Google Maps links

---

## 📋 Prerequisites

Install the following before running the project:

* Python 3.x
* pip
* Webcam
* Internet connection

The application requires internet connectivity for services such as:

* IP-based geolocation
* Push notifications
* Email alerts

---

## 🚀 Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/harshitahegde/SAFEGO_AI-Safety-Monitoring-and-alert-System.git
cd SAFEGO_AI-Safety-Monitoring-and-alert-System
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

```bash
python init_db.py
```

This creates the SQLite database required by the Flask application.

### 5. Configure Alert Services

Configure the required notification and email credentials before running the monitoring system.

For security, sensitive credentials should be stored using **environment variables** rather than being committed directly to the repository.

### 6. Run the Flask Application

```bash
python app.py
```

The Flask application will be available at:

```text
http://127.0.0.1:5000
```

### 7. Start Safety Monitoring

Run the detection system:

```bash
python detection.py
```

The application will access the webcam and begin real-time monitoring.

---

## 📂 Project Structure

```text
SAFEGO_AI-Safety-Monitoring-and-alert-System/
│
├── app.py
│
├── detection.py
│
├── init_db.py
│
├── requirements.txt
│
├── known_faces/
│   └── ...
│
├── templates/
│   └── ...
│
├── static/
│   └── ...
│
├── database/
│   └── ...
│
└── README.md
```

### `app.py`

The Flask application responsible for:

* User registration
* Login
* Logout
* Profile management
* Database interaction
* User authentication

### `detection.py`

The main computer-vision component responsible for:

* Webcam capture
* Hand landmark detection
* Signal for Help recognition
* Face recognition
* Approximate geolocation
* Evidence image capture
* Push notifications
* Email alerts
* Alert cooldown

### `init_db.py`

Initializes the SQLite database and creates the required user table.

---

## 🔄 Detection Workflow

The core monitoring process works as follows:

```text
1. Start webcam
        ↓
2. Capture video frame
        ↓
3. Detect hands using MediaPipe
        ↓
4. Analyze hand landmarks
        ↓
5. Check for Signal for Help
        ↓
6. Confirm gesture across consecutive frames
        ↓
7. Detect and identify face
        ↓
8. Retrieve approximate location
        ↓
9. Capture current frame
        ↓
10. Generate emergency message
        ↓
11. Send push notification
        ↓
12. Send email with captured frame
        ↓
13. Apply cooldown
        ↓
14. Continue monitoring
```

---

## 🛡️ Safety & Security Considerations

SafeGoAI is a prototype/academic project demonstrating the use of computer vision for safety monitoring.

Important considerations:

* IP-based location is approximate.
* Face recognition can produce incorrect matches.
* Camera quality and lighting can affect detection.
* Internet connectivity is required for external alert services.
* Emergency alerts depend on external notification and email services.
* The system should not be considered a replacement for professional emergency services.

---

## 🔒 Security Note

Sensitive information such as:

* Email passwords/app passwords
* API credentials
* Flask secret keys
* Notification credentials

should **never be committed to a public GitHub repository**.

For a production deployment, these values should be stored using environment variables or a secure secrets-management solution.

---

## 💡 Concepts Demonstrated

This project demonstrates practical experience with:

* Python programming
* Flask web development
* REST-style backend development
* Computer vision
* Hand landmark detection
* Gesture recognition
* Face recognition
* Real-time webcam processing
* Image processing with OpenCV
* SQLite database integration
* Password hashing
* Session-based authentication
* File uploads
* External API integration
* Email automation
* Push notifications
* Geolocation services
* Event-based alerting
* Cooldown/debouncing logic

---

## 🔮 Future Improvements

Possible improvements include:

* [ ] GPS-based precise location
* [ ] Mobile application integration
* [ ] More emergency gesture patterns
* [ ] Improved face-recognition accuracy
* [ ] Cloud database integration
* [ ] Secure environment-based configuration
* [ ] SMS/phone-call emergency alerts
* [ ] Emergency contact management
* [ ] Alert history and incident logging
* [ ] Admin dashboard
* [ ] Cloud deployment
* [ ] Automated testing
* [ ] Real-time monitoring dashboard

---

## 🎓 Learning Outcomes

Through SafeGoAI, the project demonstrates how multiple technologies can be combined to build a real-time safety application:

**Computer Vision + AI + Web Development + Database + External Services**

The project provided practical experience in processing live camera data, detecting human gestures, identifying users, interacting with a database, and triggering automated emergency notifications.

---



**Project:** SafeGoAI
**Type:** AI-Based Safety Monitoring System
**Built with:** Python + Flask + OpenCV + MediaPipe + SQLite
