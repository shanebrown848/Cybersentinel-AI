# 🛡️ CyberSentinel AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![AI-Powered](https://img.shields.io/badge/AI-OpenAI_GPT4-ff69b4?logo=openai)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)
![Status](https://img.shields.io/badge/Stage-Prototype-orange)
![Security](https://img.shields.io/badge/Monitoring-Anomaly%20Detection-red?logo=sklearn)

**CyberSentinel AI** is a real-time AI-powered anomaly detection tool that monitors network traffic, flags suspicious behavior, and explains anomalies using OpenAI’s GPT-4. It acts as your intelligent cybersecurity analyst—detecting, explaining, and logging threats in real time.

---

## 🚀 Features

- ⚙️ **Machine Learning-Based Anomaly Detection**  
  Trained on network traffic using Isolation Forest to flag abnormal patterns.

- 🤖 **AI Security Chatbot (GPT-4)**  
  Provides natural language analysis of detected anomalies.

- 🌐 **FastAPI-Powered Dashboard**  
  Visualize flagged events and interact with the AI assistant directly from the web.

- 🕵️‍♂️ **Live Packet Sniffing with Scapy**  
  Analyze real-time traffic and detect threats automatically.

- 🧠 **Self-Learning Engine**  
  Trains on synthetic or real data every launch to stay relevant.

---

## 📁 Project Structure

```

CyberSentinel-AI/
├── anomaly\_detector.py     # ML model + detection logic
├── api.py                  # FastAPI backend + dashboard + chat
├── chatbot.py              # OpenAI-powered explanation system
├── packet\_sniffer.py       # Live packet sniffing and detection
├── requirements.txt        # Dependencies
├── .env                    # (Not tracked) Contains API keys
└── data/
└── anomalies.db        # Local anomaly log database

````

---

## 🧪 How It Works

1. 🚦 Train the anomaly model on startup
2. 📡 Feed it live network data (or synthetic)
3. 🧠 Detect threats using Isolation Forest
4. 🤖 AI explains anomaly in plain English via GPT-4
5. 💾 Save results into a local database
6. 🌐 View & interact on the FastAPI dashboard

---

## 🛠️ Getting Started

> **Requires Python 3.10+**

```bash
# Clone the repo
git clone https://github.com/shanebrown848/Cybersentinel-AI.git
cd Cybersentinel-AI

# Set up virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env

# Start the API dashboard
python api.py
````

---

## 🌐 Web Dashboard

Access the dashboard at:

```
http://localhost:8000/
```

* 🧠 Ask the AI to explain recent anomalies
* 📊 View saved anomalies with timestamps
* 📥 Download the full log in CSV format

---

## 🔄 Optional: Live Packet Sniffing

You can run live detection using:

```bash
python packet_sniffer.py
```

This captures real-time traffic and sends detected anomalies to the AI for immediate feedback.

> ⚠️ May require `sudo` on Linux/Mac due to raw socket permissions

---



---

## 📦 Deployment Tips

* Use [Render](https://render.com) or [Replit](https://replit.com) for quick hosting
* Set `OPENAI_API_KEY` as an environment variable on the platform
* Adjust `uvicorn` command as needed:
  `uvicorn api:app --host 0.0.0.0 --port 10000`

---

## 🛡️ Security Notes

* `.env` file with API keys is **not tracked** (excluded in `.gitignore`)
* Anomalies are stored in a **local SQLite** database
* No cloud storage or uploads — your logs stay on your machine

---

## 📜 License

Licensed under the [MIT License](LICENSE).
Use it, fork it, upgrade it — just credit the original work!

---

## 🙌 Credits

Built with ❤️ by [Shane Brown](https://github.com/shanebrown848)
Made for defenders who want to use AI for good 🛡️🤖

---

```


