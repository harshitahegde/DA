**SafeGoAI** is an AI-powered surveillance and safety management platform designed to monitor environments in real-time, detect hazards, and provide instant alerts to ensure a secure workplace or public space.

## 🚀 Key Features
* **AI-Powered Detection:** Real-time monitoring using computer vision (via `detection.py`).
    *Gesture Detection(Universal Help Sign) *Face Detection
* **Instant Alerting:** Visual and system notifications when safety protocols are breached.
* **User Management:** Secure Authentication (Signup/Login) for safety officers and administrators.
* **Profile Management:** Individual user dashboards to track safety logs.
* **Responsive Web Interface:** A sleek, modern UI built with Flask, HTML5, and CSS3.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Web Framework:** Flask
* **Computer Vision:** OpenCV and  MediaPipe 
* **Database:** SQLite (Managed via `init_db.py`)
* **Frontend:** HTML5, CSS3, JavaScript

## 📂 Project Structure
* `app.py`: The central engine of the web application.
* `detection.py`: Contains the AI logic for monitoring and hazard detection.
* `init_db.py`: Script to initialize the user and alert database.
* `templates/`: UI components (`index.html`, `login.html`, `register.html`, etc.).
* `static/`: CSS and styling assets.

## ⚙️ Installation & Setup

1. **Clone the Project**
   ```bash
   git clone [https://github.com/harshitahegde/DA.git](https://github.com/harshitahegde/DA.git)
   cd SAFEGO_AI
2.**Setup Environment**
   python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3.**Install Dependencies**
pip install -r requirements.txt
4.**Initialize database**
python init_db.py
5.**Run SafeGO AI website**
python app.py
6.**Run Project**
python detection.py
