import cv2
import mediapipe as mp
import time
import math
import requests # For instant ntfy.sh alert and geolocation
import smtplib # For email alert
from email.message import EmailMessage
import datetime
import os
import numpy as np
import face_recognition # For identity recognition
import json # For handling API response

# ==============================================================================
# 🔐 --- ALERT & IDENTITY CONFIGURATION --- 
# NOTE: Credentials are hardcoded below, use a .env file for production security.
# ==============================================================================

# 1. ntfy.sh Push Notification Setup
NTFY_TOPIC = "help"
NTFY_BASE_URL = "https://ntfy.sh"
POLICE_CONTACT = "98459985753"

# 2. Email Setup (Using Gmail as an example)
SENDER_EMAIL = 'hegdetweety@gmail.com'
SENDER_PASSWORD = 'owmqpcugsstwfogp'
RECIPIENT_EMAIL = 'tweety627123@gmail.com'

# 3. System Configuration
ALERT_COOLDOWN_SECONDS = 300 # Wait 5 minutes before sending a repeat alert
CONSECUTIVE_DETECTION_FRAMES = 45 # Gesture must be held for approx 1.5 seconds

# ==============================================================================
# --- IDENTITY RECOGNITION SETUP (UNCHANGED) ---
# ==============================================================================
KNOWN_FACES_DIR = "known_faces"
UNKNOWN_PERSON_NAME = "Unknown Person"

known_face_encodings = []
known_face_names = []

print("Loading known face data...")

# Load faces from the 'known_faces' directory
if os.path.exists(KNOWN_FACES_DIR):
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            try:
                name = os.path.splitext(filename)[0]
                image = face_recognition.load_image_file(os.path.join(KNOWN_FACES_DIR, filename))
                # Check if a face is detected before encoding
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    encoding = face_encodings[0]
                    known_face_encodings.append(encoding)
                    known_face_names.append(name)
                    print(f"Loaded: {name}")
                else:
                    print(f"Warning: Could not find a face in {filename}. Skipping.")
            except Exception as e:
                print(f"Error loading {filename}: {e}. Skipping.")
else:
    print(f"Warning: '{KNOWN_FACES_DIR}' folder not found. Identity recognition will only report 'Unknown Person'.")

print("Face loading complete. Starting camera.")

# ==============================================================================
# --- MediaPipe Setup (UNCHANGED) ---
# ==============================================================================
mp_hands = mp.solutions.hands
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(model_complexity=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.7)

# ==============================================================================
# 🗺️ --- GEOLOCATION FUNCTION (NEW) ---
# ==============================================================================

def get_approximate_location():
    """Fetches approximate lat/lng based on public IP and creates a Google Maps URL."""
    try:
        # Using ipapi.co (a free tier IP geolocation service)
        response = requests.get('https://ipapi.co/json/')
        data = response.json()

        # Extract coordinates and location details
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        city = data.get('city', 'Unknown City')
        region = data.get('region', '')
        country = data.get('country_name', 'Unknown Country')
        
        location_details = f"Location: {city}, {region}, {country}"

        if latitude and longitude:
            # Google Maps URL format: https://maps.google.com/?q=lat,lng
            map_url = f"https://maps.google.com/?q={latitude},{longitude}"
            return location_details, map_url
        
        return location_details, None
    except Exception as e:
        print(f"Geolocation Error: {e}")
        return "Location: Could not determine Lat/Lng (Network Error).", None


# ==============================================================================
# --- ALERT FUNCTIONS (UPDATED) ---
# ==============================================================================

def send_urgent_ntfy_alert(title, message_body, location_url=None):
    """Sends an instant push notification via ntfy.sh."""
    try:
        headers = {
            "Title": title,
            "Priority": "urgent",
            "Tags": "warning,sos",
        }
        if location_url:
            # Add a 'click' action to the notification for quick access to the map
            headers["Actions"] = f"view, Open Map, {location_url}"
        
        response = requests.post(f"{NTFY_BASE_URL}/{NTFY_TOPIC}",
                                 data=message_body.encode('utf-8'),
                                 headers=headers)
        
        if response.status_code == 200:
            print(f"NTFY Alert Sent successfully!")
        else:
            print(f"NTFY Alert failed. Status code: {response.status_code}")

    except Exception as e:
        print(f"NTFY Error: {e}")

def send_email_alert(subject, body, image_path=None): # Removed to_email as it's a global RECIPIENT_EMAIL
    """Sends a detailed email with a captured image."""
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg.set_content(body)

        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                img_data = f.read()
            msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename=os.path.basename(image_path))

        # Using a secure connection to Gmail SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
            
        print("Email Alert Sent successfully!")
    except Exception as e:
        # Common error for Gmail: Less secure app access is disabled or 2FA/App Password is wrong
        print(f"Email Error: Could not send email. Check SENDER_EMAIL/SENDER_PASSWORD. Error: {e}")

# ==============================================================================
# --- GESTURE LOGIC (Signal for Help - UNCHANGED) ---
# ==============================================================================

def get_distance(p1, p2):
    """Calculates Euclidean distance between two MediaPipe landmarks."""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

def is_signal_for_help_gesture(hand_landmarks):
    """
    Checks the geometry for the Signal for Help (Thumb tucked, fingers closed over thumb).
    """
    
    # 1. Check if the thumb is folded *into* the palm (relative to hand size).
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    
    dist_tip_to_index = get_distance(thumb_tip, index_mcp)
    hand_size = get_distance(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST], thumb_mcp)
    
    thumb_folded_in = dist_tip_to_index / hand_size < 0.35
    
    if not thumb_folded_in:
        return False

    # 2. Check if the four fingers are folded *over* the thumb (tip closer to wrist than knuckle).
    finger_tips = [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]
    finger_mcps = [mp_hands.HandLandmark.INDEX_FINGER_MCP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP, mp_hands.HandLandmark.RING_FINGER_MCP, mp_hands.HandLandmark.PINKY_MCP]
    
    fingers_folded_count = 0
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    
    for tip_lm, mcp_lm in zip(finger_tips, finger_mcps):
        tip = hand_landmarks.landmark[tip_lm]
        mcp = hand_landmarks.landmark[mcp_lm]
        
        dist_tip_to_wrist = get_distance(tip, wrist)
        dist_mcp_to_wrist = get_distance(mcp, wrist)
        
        # Ratio < 0.8 means the finger is mostly closed.
        if dist_tip_to_wrist / dist_mcp_to_wrist < 0.8:
             fingers_folded_count += 1

    return fingers_folded_count == 4 and thumb_folded_in

# ==============================================================================
# --- MAIN LOOP (UPDATED ALERT TRIGGER) ---
# ==============================================================================

# Camera Initialization: Using index 0 and CAP_DSHOW for robustness on Windows
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Fallback: If the default camera (0) fails, try index 1
if not cap.isOpened():
    print("Default camera (index 0) failed. Trying camera index 1...")
    cap.release()
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("FATAL ERROR: Could not open camera at index 0 or 1. Check connections/permissions.")
    # Clean exit if the camera cannot be opened
    hands.close()
    exit()

gesture_frames_count = 0
last_alert_time = 0
alert_sent_for_current_event = False
recognized_identity = UNKNOWN_PERSON_NAME

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # --- State variables for this frame ---
    gesture_detected_in_frame = False
    face_detected = False
    recognized_identity = UNKNOWN_PERSON_NAME 

    # 1. Hand Detection & Gesture Check
    hand_results = hands.process(rgb_frame)
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            if is_signal_for_help_gesture(hand_landmarks):
                gesture_detected_in_frame = True
                cv2.rectangle(frame, (10, 30), (450, 70), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, "HELP SIGN DETECTED!", (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # 2. Face Detection & Recognition (ONLY if gesture is confirmed)
    if gesture_detected_in_frame:
        
        # Note: MediaPipe face detection is faster but less accurate for recognition than face_recognition
        face_locations = face_recognition.face_locations(rgb_frame)
        face_detected = len(face_locations) > 0

        if face_detected:
            # Face Encoding and Matching
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
                
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = UNKNOWN_PERSON_NAME
                
                # Find the best match
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                
                # Check match tolerance
                if matches and face_distances[best_match_index] < 0.6: 
                    name = known_face_names[best_match_index]
                
                recognized_identity = name
                
                # Draw box and label for recognized face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                
                # Update identity status text
                cv2.putText(frame, f"Identity Confirmed: {recognized_identity}", (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # 3. Temporal Smoothing and Alert Trigger
    current_time_seconds = time.time()
    
    # Alert only if gesture is present AND a face is detected
    if gesture_detected_in_frame and face_detected:
        gesture_frames_count += 1
    else:
        gesture_frames_count = 0
        alert_sent_for_current_event = False 

    if gesture_frames_count >= CONSECUTIVE_DETECTION_FRAMES and face_detected:
        
        cv2.putText(frame, "ALERT TRIGGERED - CALLING HELP", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 3)

        if not alert_sent_for_current_event and (current_time_seconds - last_alert_time) > ALERT_COOLDOWN_SECONDS:
            
            # --- New: Get Location Data ---
            location_details, location_url = get_approximate_location()

            alert_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            alert_image_filename = f"distress_alert_{alert_timestamp.replace(':', '-')}.jpg"
            cv2.imwrite(alert_image_filename, frame) 

            # 1. Send NTFY.SH Push Notification (UPDATED)
            ntfy_message_body = f"The person ({recognized_identity}) has continuously shown the 'Signal for Help' gesture. Caller contact: {POLICE_CONTACT}. Time: {alert_timestamp}. {location_details}"
            send_urgent_ntfy_alert(
                title=f"🚨 URGENT: Help Signal from {recognized_identity}!",
                message_body=ntfy_message_body,
                location_url=location_url # Pass the map URL
            )
            
            # 2. Send Email Alert (UPDATED)
            email_body = f"The user ({recognized_identity}) continuously showed the 'Signal for Help' gesture. Contact: {POLICE_CONTACT}. Time: {alert_timestamp}. {location_details}. Map Link: {location_url if location_url else 'N/A'}. Please check the attached image for visual confirmation."
            send_email_alert(
                subject=f"URGENT: Distress Signal Detected by {recognized_identity} at {alert_timestamp}",
                body=email_body,
                image_path=alert_image_filename
            )
            
            alert_sent_for_current_event = True
            last_alert_time = current_time_seconds
            print(f"\n--- ALERT CYCLE COMPLETED AT {alert_timestamp} by {recognized_identity} ---")
            
    cv2.imshow('Distress Detection System', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()