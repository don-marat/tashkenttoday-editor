FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway и Render сами подставят PORT, но для Telegram бота он не нужен, 
# бот работает через long polling
CMD ["python", "bot_v3.py"]
