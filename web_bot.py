import os, threading
from flask import Flask
app=Flask(__name__)
@app.route("/")
def home(): return "Tashkent Today Bot V4 - using openai/gpt-oss-20b (Groq 2026 models)"
@app.route("/health")
def health(): return "OK",200
def run_flask():
 port=int(os.environ.get("PORT",10000))
 app.run(host="0.0.0.0",port=port)
if __name__=="__main__":
 threading.Thread(target=run_flask, daemon=True).start()
 from bot_v4_UZ_RU import main as bot_main
 bot_main()
