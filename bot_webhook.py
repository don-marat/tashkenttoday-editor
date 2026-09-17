from flask import Flask, request
import os
import openai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import asyncio

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("prompts/SYSTEM_FINAL.md", "r", encoding="utf-8") as f:
    SYSTEM = f.read()

# Для Render/Railway - webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), None)
    # Тут вызываем твою логику 3 агентов из bot_v3.py
    # Упрощенная версия для примера
    return "ok"

@app.route("/")
def index():
    return "Tashkent Today Editor Bot is running (webhook mode)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
