from flask import Flask, request
import requests
import os
from openai import OpenAI

app = Flask(__name__)

# 🔑 Bot token & Groq API key from environment
TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# 🧠 Groq client
client = OpenAI(api_key=GROQ_API_KEY)

# 📄 Load notes
try:
    with open("notes.txt", "r", encoding="utf-8") as f:
        notes_text = f.read()
except FileNotFoundError:
    notes_text = "⚠️ Notes file not found. Please upload notes.txt."


@app.route("/")
def home():
    return "Bot is running!", 200


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # 🤖 Call Groq API
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful digital trainer. Use the notes below to answer."},
                {"role": "user", "content": f"Notes:\n{notes_text}\n\nQuestion: {text}"}
            ]
        )

        reply = response.choices[0].message.content

        payload = {
            "chat_id": chat_id,
            "text": reply
        }
        requests.post(TELEGRAM_API_URL, json=payload)

    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
