# bot.py
import asyncio
import threading
import os
from flask import Flask
from playwright.async_api import async_playwright

app = Flask(__name__)

# Добавляем маршрут для корневого URL
@app.route('/')
def index():
    return "Bot is running! Use /health to check status", 200

@app.route('/health')
def health():
    return "OK", 200

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

async def renew_server():
    print("Запускаю задачу renew server...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            page = await browser.new_page()
            
            # ВАЖНО: Замените на реальный URL Eternal Zero
            url = "https://eternal-zero.ru"  # ИЗМЕНИТЕ НА ПРАВИЛЬНЫЙ URL
            print(f"Перехожу на {url}")
            await page.goto(url, wait_until='networkidle')
            
            # Ваша логика здесь
            await asyncio.sleep(3)
            
            print("Страница загружена")
            await browser.close()
    except Exception as e:
        print(f"Ошибка в renew_server: {e}")

async def main_loop():
    while True:
        try:
            await renew_server()
            print("Задача выполнена, жду 3 часа...")
        except Exception as e:
            print(f"Ошибка в цикле: {e}")
        await asyncio.sleep(3 * 3600)  # 3 часа

if __name__ == '__main__':
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    print("Веб-сервер запущен на порту", os.environ.get('PORT', 8080))
    
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("Бот остановлен")
