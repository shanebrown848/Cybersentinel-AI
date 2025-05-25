import os
import openai
import sqlite3
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
from anomaly_detector import AnomalyDetector, generate_sample_data
from chatbot import SecurityChatbot
import uvicorn
from fastapi.responses import HTMLResponse, FileResponse
import pandas as pd
from dotenv import load_dotenv

# ✅ Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path, override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("DEBUG (api.py): Loaded API key ->", OPENAI_API_KEY)


if not OPENAI_API_KEY:
    raise ValueError("ERROR: OPENAI_API_KEY is not loaded. Check your .env file!")

openai.api_key = OPENAI_API_KEY  # ✅ Fix incorrect OpenAI client initialization

# ✅ Fix: Get the absolute path to the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FOLDER = os.path.join(BASE_DIR, "../data")
DB_PATH = os.path.join(DB_FOLDER, "anomalies.db")

# ✅ Ensure the database directory exists
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# ✅ Initialize FastAPI
app = FastAPI()
detector = AnomalyDetector()
chatbot = SecurityChatbot()

# ✅ Train model on startup
data = generate_sample_data()
detector.train(data)

# ✅ Define Pydantic model for incoming logs
class NetworkLog(BaseModel):
    packet_size: float
    response_time: float

@app.get("/")
def dashboard():
    """Return a dashboard with stored anomalies and a chatbot interface."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, ip_address, packet_size, response_time, status, explanation FROM anomalies ORDER BY timestamp DESC")
    anomalies = cursor.fetchall()
    conn.close()

    table_html = """
    <h2>Stored Anomalies</h2>
    <a href='/export_csv/' style='color: #ff6b6b; font-weight: bold;'>⬇️ Download CSV Log</a>
    <br><br>
    <table border='1' style='width: 90%; margin: auto; background-color: #2c2c3e; color: white; text-align: left;'>
        <tr>
            <th>Timestamp</th><th>IP Address</th><th>Packet Size</th><th>Response Time</th><th>Status</th><th>Explanation</th>
        </tr>
    """
    for anomaly in anomalies:
        table_html += f"<tr><td>{anomaly[0]}</td><td>{anomaly[1]}</td><td>{anomaly[2]}</td><td>{anomaly[3]}</td><td>{anomaly[4]}</td><td style='white-space: pre-wrap;'>{anomaly[5]}</td></tr>"
    table_html += "</table>"

    html_content = f"""
    <html>
    <head>
        <title>Cybersecurity Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #1e1e2f; color: white; text-align: center; }}
            h1 {{ color: #ff6b6b; }}
            table, th, td {{ border: 1px solid white; border-collapse: collapse; padding: 10px; }}
            th {{ background-color: #ff6b6b; }}
            .chatbox {{ width: 80%; margin: auto; padding: 10px; background-color: #2c2c3e; border-radius: 5px; }}
            input {{ width: 70%; padding: 10px; margin: 10px; }}
            button {{ padding: 10px; background-color: #ff6b6b; color: white; border: none; cursor: pointer; }}
            .response-box {{ margin-top: 10px; padding: 10px; background: #333; border-radius: 5px; text-align: left; }}
        </style>
    </head>
    <body>
        <h1>🔐 Cybersecurity Dashboard</h1>
        <h2>AI Security Assistant</h2>
        <div class="chatbox">
            <input type="text" id="userInput" placeholder="Ask about network anomalies..." onkeypress="handleKeyPress(event)" />
            <button onclick="sendQuestion()">Ask AI</button>
            <div id="response" class="response-box"></div>
        </div>
        <br><hr><br>
        {table_html}
        <script>
            function handleKeyPress(event) {{
                if (event.key === "Enter") {{
                    sendQuestion();
                }}
            }}

            async function sendQuestion() {{
                let question = document.getElementById("userInput").value;
                let responseBox = document.getElementById("response");

                responseBox.innerHTML = "⏳ Thinking...";

                let response = await fetch("/chat/", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{ "question": question }})
                }});

                let data = await response.json();
                responseBox.innerHTML = "🔍 <b>AI Response:</b> " + data.response;
                document.getElementById("userInput").value = ""; // Clear input field after sending question
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat/")
async def chat_with_ai(request: Request):
    """API endpoint to interact with OpenAI for AI-powered responses."""
    try:
        data = await request.json()
        user_question = data.get("question", "").strip()

        if not user_question:
            return {"response": "❌ Please ask a valid question."}

        # ✅ Fetch the latest 10 anomalies from the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, ip_address, packet_size, response_time, status, explanation FROM anomalies ORDER BY timestamp DESC LIMIT 10")
        anomalies = cursor.fetchall()
        conn.close()

        # ✅ Format anomaly data as context
        anomaly_context = "\n".join([f"{a[0]} | {a[1]} | {a[2]} bytes | {a[3]} ms | {a[4]} | {a[5]}" for a in anomalies])

        # ✅ Create prompt for OpenAI
        prompt = f"""
        You are a cybersecurity AI. Answer user questions based on the following network anomalies:

        {anomaly_context}

        User's Question: {user_question}
        """

        # ✅ Call OpenAI API
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an expert cybersecurity assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=500
        )

        ai_response = response.choices[0].message.content.strip()
        return {"response": ai_response if ai_response else "⚠️ AI failed to generate a response."}

    except Exception as e:
        print("❌ AI Error:", str(e))
        return {"response": f"⚠️ AI Connection Failed: {str(e)}"}

@app.get("/export_csv/")
def export_csv():
    """Export anomaly data to CSV."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM anomalies", conn)
    conn.close()
    file_path = "./anomalies_export.csv"
    df.to_csv(file_path, index=False)
    return FileResponse(file_path, media_type="text/csv", filename="anomalies.csv")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
