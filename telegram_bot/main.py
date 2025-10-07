"""
Telegram Bot Main - Flask приложение с webhook
"""

import os
import sys
import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from bot import create_application

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telegram bot
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not set!")
    sys.exit(1)

# Создаем Telegram application
telegram_app = create_application(BOT_TOKEN)


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "service": "telegram-bti-bot"
    })


@app.route('/webhook', methods=['POST'])
async def webhook():
    """Webhook endpoint для Telegram"""
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        await telegram_app.process_update(update)
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.exception(f"❌ Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/set-webhook', methods=['POST'])
def set_webhook():
    """Устанавливает webhook для Telegram"""
    try:
        webhook_url = os.environ.get("WEBHOOK_URL")
        if not webhook_url:
            webhook_url = f"https://telegram-bti-bot-637190449180.europe-west1.run.app/webhook"
        
        # Устанавливаем webhook
        import requests
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        response = requests.post(url, json={"url": webhook_url})
        
        return jsonify({
            "status": "success",
            "webhook_url": webhook_url,
            "telegram_response": response.json()
        })
    except Exception as e:
        logger.exception(f"❌ Error setting webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/', methods=['POST'])
async def index():
    """Главный endpoint (alias для webhook)"""
    return await webhook()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    # Логирование запуска
    logger.info("=" * 50)
    logger.info("🤖 Telegram BTI Bot starting...")
    logger.info(f"   Port: {port}")
    logger.info(f"   GCS Bucket: {GCS_BUCKET}")
    logger.info("=" * 50)
    
    # Запуск Flask
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', port, app, use_reloader=False, use_debugger=False)

