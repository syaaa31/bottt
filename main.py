import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from openai import OpenAI
import asyncio

# 🔑 Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 🌟 Groq API client
client = OpenAI(
    api_key=GROQ_API_KEY,
    api_base="https://api.groq.com/v1"
)

# 📄 Load notes
try:
    with open("notes.txt", "r", encoding="utf-8") as f:
        notes_text = f.read()
except FileNotFoundError:
    notes_text = "⚠️ Notes file not found. Please upload notes.txt."

# 🔹 Flask app
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
# Create the Application for p-t-b
application = ApplicationBuilder().token(BOT_TOKEN).build()

# 👋 /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Haii everyone! 👋\nI'm your hybrid digital trainer AI bot 🤖\n\n"
        "Ask me anything based on the notes!"
    )

# 💬 Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_question = update.message.text

    # Show typing action
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # Request to Groq
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful digital trainer. Use the notes below to answer."},
            {"role": "user", "content": f"Notes:\n{notes_text}\n\nQuestion: {user_question}"}
        ]
    )
    bot_reply = response.choices[0].message.content
    await update.message.reply_text(bot_reply)

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🔹 Flask webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    asyncio.run(application.update_queue.put(update))
    return "OK"

# 🔹 Flask root
@app.route("/")
def index():
    return "Bot is running ✅"

# ▶️ Run Flask (Render web service)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
