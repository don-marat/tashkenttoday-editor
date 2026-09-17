import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import openai

# Загрузи промт
with open("prompts/SYSTEM_FINAL.md", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    if not raw_text or len(raw_text) < 20:
        return

    # Показываем что бот думает
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw_text}
        ],
        temperature=0.3
    )

    news = response.choices[0].message.content

    # Отправляем в ту же группу готовую новость
    await update.message.reply_text(news, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Tashkent Today Editor Bot запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
