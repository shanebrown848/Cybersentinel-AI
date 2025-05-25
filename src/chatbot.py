import os
import openai
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path, override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("DEBUG (chatbot.py): Loaded API key ->", OPENAI_API_KEY)

if not OPENAI_API_KEY:
    raise ValueError("ERROR: OPENAI_API_KEY is not loaded. Check your .env file!")

openai.api_key = OPENAI_API_KEY

class SecurityChatbot:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        openai.api_key = self.api_key  # Fix incorrect OpenAI client initialization

    def respond(self, alert_message):
        """Send network anomaly details to OpenAI for analysis."""
        if not self.api_key:
            return "⚠️ API Key not found. Please configure OpenAI API."

        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a cybersecurity AI that explains network anomalies."},
                    {"role": "user", "content": f"Analyze this security event and provide a structured summary: {alert_message}"}
                ],
                temperature=0.5,
                max_tokens=300
            )
            # return response.choices[0].message.content.strip()
        
            raw_response = response.choices[0].message.content.strip()
            formatted_response = raw_response.replace("\n", "<br>")
            
            return f"<div style='text-align: left; padding: 10px; font-size: 14px;'><b>🔍 AI Response:</b><br>{formatted_response}</div>"

        except Exception as e:
            return f"⚠️ AI Connection Failed: {str(e)}"
