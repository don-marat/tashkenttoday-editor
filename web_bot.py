
import os
import threading
from flask import Flask
from bot_v4_UZ_RU import main as bot_main

app = Flask(__name__)

@app.route("/")
def home():
    return "Tashkent Today Editor Bot is running! UZ->RU + 3 agents"

@app.route("/health")
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot_main()
