import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
from openai import OpenAI
import time
import threading

# 🔑 Load secrets from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/v1"  # your Groq endpoint

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, use_context=True)

# 📄 Load notes from file
try:
    with open("notes.txt", "r", encoding="utf-8") as f:
        notes_text = f.read()
except FileNotFoundError:
    notes_text = "⚠️ Notes file not found. Please upload notes.txt."

# Initialize Groq client
client = OpenAI(api_key=GROQ_API_KEY, api_base=GROQ_URL)

# 👋 /start command
def start(update, context):
    update.message.reply_text(
        "Haii everyone! 👋\nI'm your hybrid digital trainer AI bot 🤖\n\n"
        "Ask me anything based on the notes!"
    )

# 💬 Handle questions with typing simulation
def handle_message(update, context):
    user_question = update.message.text
    chat_id = update.message.chat_id

    # Simulate typing
    def send_typing():
        bot.send_chat_action(chat_id=chat_id, action="typing")
        time.sleep(1)  # simulate delay

    typing_thread = threading.Thread(target=send_typing)
    typing_thread.start()

    # Request Groq API
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful digital trainer. Use the notes below to answer."},
            {"role": "user", "content": f"Notes:\n{notes_text}\n\nQuestion: {user_question}"}
        ]
    )

    typing_thread.join()
    bot_reply = response.choices[0].message.content
    update.message.reply_text(bot_reply)

# 🚀 Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🔗 Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# ▶️ Health check
@app.route("/")
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
