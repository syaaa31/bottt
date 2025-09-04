import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from openai import OpenAI

# 🔑 Get secrets from Render environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ✅ Correctly configure Groq endpoint
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# 📄 Load notes once when bot starts
try:
    with open("notes.txt", "r", encoding="utf-8") as f:
        notes_text = f.read()
except FileNotFoundError:
    notes_text = "⚠️ Notes file not found. Please upload notes.txt."

# 👋 /start command
async def start(update, context):
    await update.message.reply_text(
        "Haii everyone! 👋\nI'm your hybrid digital trainer AI bot 🤖\n\n"
        "Ask me anything based on the notes!"
    )

# 💬 Handle student questions
async def handle_message(update, context):
    user_question = update.message.text

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # fast Groq model
        messages=[
            {"role": "system", "content": "You are a helpful digital trainer. Use the notes below to answer."},
            {"role": "user", "content": f"Notes:\n{notes_text}\n\nQuestion: {user_question}"}
        ]
    )

    bot_reply = response.choices[0].message.content
    await update.message.reply_text(bot_reply)

# 🚀 Bot setup
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ▶️ Entry point for Render background worker
if __name__ == "__main__":
    app.run_polling()
