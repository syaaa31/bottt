# 📌 Imports
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)
from openai import OpenAI
import nest_asyncio
import asyncio

# 🧠 Your Groq API setup
client = OpenAI(
    api_key="GROQ_API_KEY",   # 🔑 Replace with your Groq API key
    base_url="https://api.groq.com/openai/v1"
)

# 📄 Load your notes from a file
with open("notes.txt", "r", encoding="utf-8") as f:
    notes_text = f.read()

# 🤖 AI answer function using notes
def ask_question(question: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful digital trainer. Use the following notes to answer student questions."
        },
        {
            "role": "user",
            "content": f"Notes:\n{notes_text}\n\nQuestion: {question}"
        }
    ]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return response.choices[0].message.content

# 👋 /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Haii everyone!👋\n I'm your hybrid digital electronic trainer AI chatbot🤖\n\n"
        "You can ask me anything based on our module notes!"
    )

# 💬 Normal message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(1.5)
    answer = ask_question(user_question)
    await update.message.reply_text(answer)

# 🚀 Telegram Bot Setup
BOT_TOKEN = "BOT_TOKEN"   # 🔑 Replace with your BotFather token
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🛠 Fix Colab event loop
nest_asyncio.apply()

# ▶️ Async main loop
# ▶️ Async main loop
async def main():
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


