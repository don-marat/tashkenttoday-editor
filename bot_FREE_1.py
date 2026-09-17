import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# GROQ - бесплатно, быстро, без карты
# Получить ключ: https://console.groq.com/keys
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

with open("prompts/SYSTEM_FINAL.md", "r", encoding="utf-8") as f:
    SYSTEM = f.read()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    if not raw_text or len(raw_text) < 20 or raw_text.startswith("/"):
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Бесплатная и очень быстрая модель, лучше чем gpt-4o-mini для редактуры
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": raw_text}
        ],
        temperature=0.3
    )
    
    news = completion.choices[0].message.content
    await update.message.reply_text(news, parse_mode="Markdown")

def main():
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("FREE Bot (Groq + Telegram) запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
