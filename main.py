import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.constants import ChatAction
from openai import OpenAI

# 🔑 Get secrets from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PORT = int(os.getenv("PORT", 8000))  # Fake port for Render

# 🌐 OpenAI client (Groq)
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.ai/v1"
)

# 📄 Load notes
try:
    with open("notes.txt", "r", encoding="utf-8") as f:
        notes_text = f.read()
except FileNotFoundError:
    notes_text = "⚠️ Notes file not found. Please upload notes.txt."

# 👋 /start
async def start(update, context):
    await update.message.reply_text(
        "Haii everyone! 👋\nI'm your hybrid digital trainer AI bot 🤖\n\n"
        "Ask me anything based on the notes!"
    )

# 💬 Handle questions
async def handle_message(update, context):
    user_question = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful digital trainer. Use the notes below to answer."},
            {"role": "user", "content": f"Notes:\n{notes_text}\n\nQuestion: {user_question}"}
        ]
    )
    bot_reply = response.choices[0].message.content
    await update.message.reply_text(bot_reply)

# 🚀 Telegram bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🖥 Dummy HTTP server for Render
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_dummy_server():
    httpd = HTTPServer(("", PORT), DummyHandler)
    httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ▶️ Start bot
if __name__ == "__main__":
    app.run_polling()
