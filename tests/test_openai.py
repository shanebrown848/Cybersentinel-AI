import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("🔍 Loaded API Key:", "FOUND" if OPENAI_API_KEY else "NOT FOUND")

if not OPENAI_API_KEY:
    raise ValueError("⚠️ ERROR: OPENAI_API_KEY is not loaded. Check your .env file!")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Test request to OpenAI
try:
    response = client.models.list()  # Fetch available models
    print("\n✅ API Key is working! List of available models:")
    for model in response.data:
        print(f" - {model.id}")

except Exception as e:
    print(f"❌ API Test Failed: {str(e)}")
