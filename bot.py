# bot.py
import asyncio
import threading
import os
from flask import Flask
from playwright.async_api import async_playwright
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running! Use /health to check status", 200

@app.route('/health')
def health():
    return "OK", 200

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# ⭐ ВАШИ COOKIES ИЗ БРАУЗЕРА (только нужные для авторизации)
COOKIES = [
    {
        "name": "eternalzero-session",
        "value": "eyJpdiI6IlYycHREbDh3b0NFNTVvZzBrYVF2QWc9PSIsInZhbHVlIjoiemRrRGpEcUtLeEt2Wjk1aVp4NC9tKzN2RjBRNmF5cE9IektiR2d6T2w4d1ZnQXpzaGFyQXBoditRUytydkhXZWVOQ2RGSGxLZkpPSFhETHVSSzZ1TkltRVNQenE1MG5iSGlUd2tJd0k0Rmhud0QyNG5HQkZFb3VBV0FJL3pWUkciLCJtYWMiOiJmZDI2NjU4MWIyZjc1Zjc2Zjc3MTBlNGY0OGJkOTUxODI0YTAxMGU5MTIwZTU0MTcyYWM5NjgzNGRlOWQ4M2E5IiwidGFnIjoiIn0=",
        "domain": "eternalzero.cloud",
        "path": "/",
        "httpOnly": True,
        "secure": True,
        "sameSite": "Lax"
    },
    {
        "name": "XSRF-TOKEN",
        "value": "eyJpdiI6IktYeTY1d2poQ05XWnlBSW1GYWRMRmc9PSIsInZhbHVlIjoiSGk3bG93MGl0cnBPU1MzdzJZaFZzdkgzOWR5UUhZR0RnMjU4OFA4Tm5OWXhJM1Vra2g3dkRxdGpyV09JcjRGeC9Dc0cyd3JWTnZ0WmpOVFdxK3Y5Q2I2b2JZQkZrUHA3RGdDQ3F3MW0rNGlKMkY1Unp2ZU0rYXRRUERocnJ2NnkiLCJtYWMiOiI1OWIxYWNhNjNjNjIwOTNmNDExNTQzZWRjNmFmNjg0MTg3MTkzNzljZDEyMDcwMjlhYjdiZGI0YjVlNTlkNjcxIiwidGFnIjoiIn0=",
        "domain": "eternalzero.cloud",
        "path": "/",
        "httpOnly": False,
        "secure": True,
        "sameSite": "Lax"
    }
]

async def solve_hcaptcha(page):
    """Решение hCaptcha"""
    try:
        print("Ожидаю появления hCaptcha...")
        
        # Ждем iframe hCaptcha
        iframe = await page.wait_for_selector('iframe[src*="hcaptcha.com"]', timeout=10000)
        frame = await iframe.content_frame()
        
        if frame:
            # Кликаем на чекбокс
            checkbox = await frame.wait_for_selector('.checkbox', timeout=5000)
            await checkbox.click()
            print("✅ Чекбокс hCaptcha нажат")
            
            # Ждем решения (3 секунды)
            await page.wait_for_timeout(3000)
            
            # Получаем токен
            token = await page.evaluate('hcaptcha.getResponse()')
            if token:
                print(f"✅ Получен hCaptcha токен: {token[:30]}...")
                return token
            
        return None
        
    except Exception as e:
        print(f"⚠️ Ошибка при решении hCaptcha: {e}")
        return None

async def renew_server():
    print("=" * 60)
    print(f"🚀 Запуск задачи: {datetime.now()}")
    print("=" * 60)
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage'
                ]
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Устанавливаем cookies
            await context.add_cookies(COOKIES)
            print(f"✅ Загружено {len(COOKIES)} cookies")
            
            page = await context.new_page()
            
            # Переходим на страницу сервера
            url = 'https://eternalzero.cloud/servers/232/info'
            print(f"🌐 Перехожу: {url}")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            await page.wait_for_timeout(3000)
            
            # Проверяем авторизацию
            if 'login' in page.url.lower():
                print("❌ ОШИБКА: Не удалось авторизоваться! Cookies устарели.")
                await page.screenshot(path='auth_failed.png')
                return
            
            print("✅ Авторизация успешна!")
            await page.screenshot(path='page_loaded.png')
            
            # Решаем hCaptcha, если есть
            hcaptcha_exists = await page.query_selector('.h-captcha')
            if hcaptcha_exists:
                print("🔐 Обнаружена hCaptcha, решаем...")
                token = await solve_hcaptcha(page)
                if token:
                    # Вставляем токен в скрытое поле
                    await page.evaluate(f"""
                        const input = document.querySelector('[name="h-captcha-response"]');
                        if (input) input.value = '{token}';
                    """)
                    print("✅ hCaptcha токен вставлен")
                else:
                    print("⚠️ Не удалось решить hCaptcha, пробуем продолжить...")
            
            # Ищем и нажимаем кнопку Renew
            print("🔍 Ищу кнопку Renew Server...")
            
            # Ждем появления кнопки
            await page.wait_for_selector('#renew-button', timeout=10000)
            
            # Кликаем
            await page.click('#renew-button')
            print("✅ Кнопка Renew Server нажата!")
            
            # Ждем ответа
            await page.wait_for_timeout(5000)
            
            # Проверяем результат по тексту на странице
            content = await page.content()
            
            if 'success' in content.lower() or 'renewed' in content.lower():
                print("✅✅✅ СЕРВЕР УСПЕШНО ПРОДЛЕН! ✅✅✅")
            elif 'daily limit' in content.lower() or 'renewal limit' in content.lower():
                print("⚠️ Достигнут лимит продлений на сегодня")
            elif 'discord' in content.lower():
                print("⚠️ Требуется подключение Discord аккаунта")
            else:
                print("❓ Результат неизвестен, проверьте скриншот")
            
            await page.screenshot(path='result.png')
            await browser.close()
            
            print(f"✅ Задача завершена: {datetime.now()}")
            
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

async def main_loop():
    """Основной цикл: запускается каждые 3 часа"""
    # Запускаем сразу при старте
    await renew_server()
    
    while True:
        print(f"⏰ Следующая задача через 3 часа ({datetime.now()})")
        await asyncio.sleep(3 * 3600)  # 3 часа
        await renew_server()

if __name__ == '__main__':
    # Запускаем веб-сервер для пингов
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    print("🌐 Веб-сервер запущен на порту", os.environ.get('PORT', 8080))
    print("🤖 Бот запущен, начинаю работу...")
    
    # Запускаем основной цикл
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен пользователем")
