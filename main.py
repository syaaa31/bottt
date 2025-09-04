import os
import time
from flask import Flask, request
from telegram import Bot, Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from openai import OpenAI

# 🔑 Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize bot
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

# 👋 /start command
async def start(update: Update, context):
    await update.message.reply_text(
        "Haii everyone! 👋\nI'm your hybrid digital trainer AI bot 🤖\n\n"
        "Ask me anything based on the notes!"
    )

# 💬 Handle user messages
async def handle_message(update: Update, context):
    user_question = update.message.text

    # Simulate typing
    await bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    time.sleep(1)  # simulate delay

    # Call Groq API
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful digital trainer. Use the notes below to answer."},
            {"role": "user", "content": f"Notes:\n{notes_text}\n\nQuestion: {user_question}"}
        ]
    )

    bot_reply = response.choices[0].message.content
    await update.message.reply_text(bot_reply)

# Telegram application (dispatcher)
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask route for webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put(update)
    return "ok", 200

# Root route
@app.route("/")
def index():
    return "Bot is running!", 200

# ▶️ Run Flask app (only for local testing; Render uses gunicorn)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
