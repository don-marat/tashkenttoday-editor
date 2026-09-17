import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import openai
from dotenv import load_dotenv

load_dotenv()

# Загружаем 3 промта
def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

PROMPT_JOURNALIST = load_prompt("prompts/01_journalist.md")
PROMPT_EDITOR = load_prompt("prompts/02_editor.md")
PROMPT_TITLES = load_prompt("prompts/03_title_gen.md")

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_agent(system_prompt, user_content, temp=0.3):
    # Запускаем в отдельном потоке чтобы не блокировать бота
    def _call():
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
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
    if not raw_text or len(raw_text) < 30: # игнор коротких
        return
    if raw_text.startswith("/"):
        return

    chat_id = update.effective_chat.id
    # Индикатор набора
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    status_msg = await update.message.reply_text("⏳ Прогоняю через 3 агентов: журналист → редактор → заголовки...")

    try:
        # АГЕНТ 1: Журналист (вытаскивает факты)
        draft = await run_agent(PROMPT_JOURNALIST, raw_text, temp=0.4)
        await status_msg.edit_text(f"✅ Агент 1 (Журналист) готов.\n\n{draft[:300]}...\n\n⏳ Агент 2: режу воду...")
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        # АГЕНТ 2: Редактор-фактчекер (режет 40-60%)
        edited = await run_agent(PROMPT_EDITOR, f"ИСХОДНИК:\n{raw_text}\n\nЧЕРНОВИК ЖУРНАЛИСТА:\n{draft}", temp=0.2)
        await status_msg.edit_text(f"✅ Агент 2 (Редактор) готов.\n\n⏳ Агент 3: генерю заголовки...")
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        # АГЕНТ 3: Заголовки + финальная сборка
        final_news = await run_agent(PROMPT_TITLES, edited, temp=0.5)

        # Удаляем статус и отправляем итог
        await status_msg.delete()
        await update.message.reply_text(final_news, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {e}")

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN не найден в .env")
    
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Tashkent Today V3 (3 agents) запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
