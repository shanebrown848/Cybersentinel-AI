from scapy.all import sniff, IP
import pandas as pd
import numpy as np
import sqlite3
import re
from datetime import datetime
from anomaly_detector import AnomalyDetector, generate_sample_data
from chatbot import SecurityChatbot
import os
from ipaddress import ip_address

# Initialize anomaly detector & chatbot
detector = AnomalyDetector()
chatbot = SecurityChatbot()

# Train the model on startup
data = generate_sample_data()
detector.train(data)

# Fix: Ensure database path is correct
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../data/anomalies.db")

def format_ip(ip):
    try:
        return str(ip_address(ip))
    except ValueError:
        print(f"⚠️ Invalid IP detected: {ip}, skipping....")
        return None

def save_anomaly(ip_address, packet_size, response_time, explanation):
    """Save detected anomalies in the database, ensuring correct timestamping."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allow fetching results with column names
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Generate timestamp

    print(f"🟢 Attempting to save anomaly: {ip_address}, {packet_size}, {response_time}, {explanation}, {timestamp}")

    try:
    
        cursor.execute(
            "INSERT INTO anomalies (ip_address, packet_size, response_time, status, explanation, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (ip_address, packet_size, response_time, "Anomaly", explanation, timestamp)
        )

        conn.commit()
        print("✅ Anomaly successfully saved in database!")

    except Exception as e:
        print(f"❌ ERROR saving to database: {e}")

    finally:
        conn.close()

def packet_callback(packet):
    """Process captured network packets and store anomalies."""
    try:
        if IP in packet:
            packet_size = len(packet)  # Packet size
            response_time = np.random.uniform(50, 200)  # Simulated response time
            ip_address = format_ip(packet[IP].src)
            
            if not ip_address:
                return 

            # ✅ Validate IP Address Format (Fix Malformed IP Issue)
            if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_address):
                print(f"⚠️ Skipping malformed IP: {ip_address}")
                return

            # ✅ Create a DataFrame for anomaly detection
            data = pd.DataFrame([[packet_size, response_time]], columns=["PacketSize", "ResponseTime"])

            # ✅ Predict if it's an anomaly
            prediction = detector.predict(data)[0]

            if prediction == "Anomaly":
                # ✅ Trigger chatbot for explanation
                alert_message = f"🚨 Unusual activity detected: IP={ip_address}, PacketSize={packet_size}, ResponseTime={response_time}"
                chatbot_response = chatbot.respond(alert_message)

                # ✅ Save anomaly in the database (Now includes timestamp)
                save_anomaly(ip_address, packet_size, response_time, chatbot_response)

                print(f"🚨 Anomaly Detected & Stored: IP={ip_address}, PacketSize={packet_size}, ResponseTime={response_time}")
                print(f"🤖 Chatbot Response: {chatbot_response}")
            else:
                print(f"✅ Normal Traffic: IP={ip_address}, PacketSize={packet_size}, ResponseTime={response_time}")

    except Exception as e:
        print(f"❌ Error processing packet: {str(e)}")

# ✅ Run packet sniffing for 30 seconds
print("🚀 Listening for network traffic for 30 seconds...")
sniff(prn=packet_callback, store=False, timeout=30)
print("✅ Stopped sniffing after 30 seconds.")
