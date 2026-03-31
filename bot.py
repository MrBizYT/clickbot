# bot.py
import asyncio
import threading
from flask import Flask
from playwright.async_api import async_playwright

app = Flask(__name__)

# Простая страница для проверки здоровья бота
@app.route('/health')
def health():
    return "OK", 200

def run_web():
    app.run(host='0.0.0.0', port=8080)

# Функция, которая делает ваше дело — капча и кнопка
async def renew_server():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Идем на сайт Eternal Zero
        await page.goto('https://eternal-zero.ru')  # пример
        
        # Здесь логика прохождения капчи и нажатия кнопки
        # ... (ваш код)
        
        await browser.close()

# Основной цикл: каждые 3 часа запускаем задачу
async def main_loop():
    while True:
        try:
            await renew_server()
        except Exception as e:
            print(f"Ошибка: {e}")
        await asyncio.sleep(3 * 3600)  # 3 часа

if __name__ == '__main__':
    # Запускаем веб-сервер в отдельном потоке
    threading.Thread(target=run_web, daemon=True).start()
    
    # Запускаем основной цикл
    asyncio.run(main_loop())
