import sqlite3
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from chatbot import SecurityChatbot
import os
from datetime import datetime

class AnomalyDetector:
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.model = IsolationForest(n_estimators=200, contamination=0.03, random_state=42)
        self.scaler = StandardScaler()
        self.chatbot = SecurityChatbot()
        db_path = os.path.join(os.path.dirname(__file__), "../data/anomalies.db")
        self.db_connection = sqlite3.connect(db_path)
        self.cursor = self.db_connection.cursor()
        self.create_table()

    def create_table(self):
        """ Create a database table for storing detected anomalies. """
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS anomalies (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                               ip_address TEXT,
                               packet_size REAL,
                               response_time REAL,
                               status TEXT,
                               explanation TEXT
                               )''')
        self.db_connection.commit()

    def save_anomaly(self, ip_address, packet_size, response_time, explanation):
        """ Save detected anomalies to the database with timestamps. """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Generate timestamp
        self.cursor.execute(
            "INSERT INTO anomalies (timestamp, ip_address, packet_size, response_time, status, explanation) VALUES (?, ?, ?, ?, ?, ?)", 
            (timestamp, ip_address, packet_size, response_time, "Anomaly", explanation)
        )
        self.db_connection.commit()

    def train(self, data):
        """ Train the model on network traffic data. """
        scaled_data = self.scaler.fit_transform(data)
        self.model.fit(scaled_data)

    def predict(self, data):
        """ Predict anomalies in network traffic data. """
        scaled_data = self.scaler.transform(data)
        predictions = self.model.predict(scaled_data)
        return np.where(predictions == -1, "Anomaly", "Normal")

    def analyze_and_respond(self, data):
        """ Detect anomalies, store them, and trigger chatbot responses. """
        predictions = self.predict(data)
        data["Status"] = predictions

        for index, row in data.iterrows():
            if row["Status"] == "Anomaly":
                alert_message = f"🚨 Unusual activity detected: PacketSize={row['PacketSize']}, ResponseTime={row['ResponseTime']}"
                response = self.chatbot.respond(alert_message)
                print("\n🚨 ALERT:", alert_message)
                print("🤖 Chatbot Response:", response)

                # Save anomaly to the database
                self.save_anomaly(row["PacketSize"], row["ResponseTime"], "Anomaly", response)

# Generate sample data
def generate_sample_data():
    np.random.seed(42)
    normal_traffic = np.random.normal(loc=50, scale=15, size=(100, 2))
    attack_traffic = np.random.normal(loc=100, scale=20, size=(10, 2))
    data = np.vstack((normal_traffic, attack_traffic))
    df = pd.DataFrame(data, columns=["PacketSize", "ResponseTime"])
    return df

if __name__ == "__main__":
    data = generate_sample_data()
    detector = AnomalyDetector()
    detector.train(data)
    detector.analyze_and_respond(data)
