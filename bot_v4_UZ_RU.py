import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from groq import Groq
from dotenv import load_dotenv
import asyncio

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

PROMPT_TRANSLATOR = load_prompt("prompts/00_translator.md")
PROMPT_JOURNALIST = load_prompt("prompts/01_journalist.md")
PROMPT_EDITOR = load_prompt("prompts/02_editor.md")
PROMPT_TITLES = load_prompt("prompts/03_title_gen.md")

async def run_agent(system_prompt, user_content, temp=0.3):
    def _call():
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=temp
        )
        return resp.choices[0].message.content
    return await asyncio.to_thread(_call)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    if not raw_text or len(raw_text) < 20 or raw_text.startswith("/"):
        return

    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    status_msg = await update.message.reply_text("🌐 Проверяю язык...")

    try:
        # АГЕНТ 0: Переводчик UZ -> RU
        translated = await run_agent(PROMPT_TRANSLATOR, raw_text, temp=0.1)
        is_uz = translated.strip() != raw_text.strip() and len(raw_text) > 0
        if is_uz:
            await status_msg.edit_text(f"🌐 Обнаружен узбекский, перевожу...\n\n{translated[:300]}...")
        else:
            translated = raw_text
            await status_msg.edit_text("✅ Русский, перевожу не нужно. ⏳ Агент 1: журналист...")
        
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        # АГЕНТ 1: Журналист
        draft = await run_agent(PROMPT_JOURNALIST, translated, temp=0.4)
        await status_msg.edit_text(f"✅ Агент 1 готов.\n⏳ Агент 2: режу воду...")
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        # АГЕНТ 2: Редактор
        edited = await run_agent(PROMPT_EDITOR, f"ИСХОДНИК:\n{translated}\n\nЧЕРНОВИК:\n{draft}", temp=0.2)
        await status_msg.edit_text(f"✅ Агент 2 готов.\n⏳ Агент 3: заголовки...")
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        # АГЕНТ 3: Заголовки
        final_news = await run_agent(PROMPT_TITLES, edited, temp=0.5)

        await status_msg.delete()
        await update.message.reply_text(final_news, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {e}")

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN не найден")
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Tashkent Today V4 (UZ->RU + 3 agents) запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
