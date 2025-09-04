import os
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.constants import ChatAction
from openai import OpenAI

# 🔑 Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Groq client
client = OpenAI(api_key=GROQ_API_KEY)

# 📄 Load notes
try:
    with open("notes.txt", "r", encoding="utf-8") as f:
        notes_text = f.read()
except FileNotFoundError:
    notes_text = "⚠️ Notes file not found. Please upload notes.txt."

# 🔹 Helper async function to process messages
async def process_message(chat_id, user_question):
    # Show typing
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(1)  # non-blocking delay

    # Call Groq API
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful digital trainer. Use the notes below to answer."},
            {"role": "user", "content": f"Notes:\n{notes_text}\n\nQuestion: {user_question}"}
        ]
    )

    bot_reply = response.choices[0].message.content
    await bot.send_message(chat_id=chat_id, text=bot_reply)

# 👋 Handle /start command
@app.route(f"/{BOT_TOKEN}/start", methods=["POST"])
def start_command():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    chat_id = update.effective_chat.id
    bot.send_message(
        chat_id=chat_id,
        text="Haii everyone! 👋\nI'm your hybrid digital trainer AI bot 🤖\n\nAsk me anything based on the notes!"
    )
    return "ok", 200

# 💬 Handle all other messages
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    chat_id = update.effective_chat.id
    user_text = update.message.text

    # Run the async function in the background
    asyncio.run(process_message(chat_id, user_text))

    return "ok", 200

# Root route
@app.route("/")
def index():
    return "Bot is running!", 200

# ▶️ Run Flask app locally
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
