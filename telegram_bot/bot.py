"""
Telegram Bot логика для обработки DWG файлов
"""

import os
import logging
import tempfile
import uuid
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google.cloud import storage
from api_client import DWGProcessorClient

logger = logging.getLogger(__name__)

# GCS настройки
GCS_BUCKET = os.environ.get("GCS_BUCKET", "btibot-processed")

# API клиент для dwg-processor-core
processor_client = DWGProcessorClient()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    welcome_message = (
        "👋 <b>Добро пожаловать в BTI DWG Processor!</b>\n\n"
        "📐 Я обрабатываю DWG файлы с применением BTE шаблона.\n\n"
        "📤 <b>Как использовать:</b>\n"
        "1. Отправьте мне DWG файл\n"
        "2. Я обработаю его через Autodesk APS\n"
        "3. Вы получите готовый DWG с примененным шаблоном\n\n"
        "⏱️ Обработка занимает ~5-10 секунд\n\n"
        "Попробуйте отправить DWG файл! 🚀"
    )
    
    await update.message.reply_text(welcome_message, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = (
        "ℹ️ <b>Помощь - BTI DWG Processor</b>\n\n"
        "<b>Команды:</b>\n"
        "/start - Главное меню\n"
        "/help - Эта справка\n"
        "/status - Проверить статус сервиса\n\n"
        "<b>Обработка файлов:</b>\n"
        "• Отправьте DWG файл как документ\n"
        "• Получите обработанный DWG с BTE шаблоном\n\n"
        "🔧 Powered by Autodesk APS"
    )
    
    await update.message.reply_text(help_text, parse_mode='HTML')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status - проверка сервиса"""
    await update.message.reply_text("🔍 Проверяю статус сервиса...")
    
    # Проверка dwg-processor-core
    health = processor_client.health_check()
    
    if health.get("status") == "ok":
        status_message = (
            "✅ <b>Сервис работает!</b>\n\n"
            f"🚀 DWG Processor Core: OK\n"
            f"📊 Service: {health.get('service')}\n\n"
            "Готов к обработке файлов! 🎉"
        )
    else:
        status_message = (
            "⚠️ <b>Проблемы с сервисом</b>\n\n"
            f"❌ DWG Processor Core: {health.get('message')}\n\n"
            "Попробуйте позже или обратитесь к администратору."
        )
    
    await update.message.reply_text(status_message, parse_mode='HTML')


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка загруженного DWG файла"""
    try:
        document = update.message.document
        
        # Проверяем что это DWG
        if not document.file_name.lower().endswith('.dwg'):
            await update.message.reply_text(
                "❌ Пожалуйста, отправьте DWG файл.\n"
                "Расширение файла должно быть .dwg"
            )
            return
        
        await update.message.reply_text(
            f"📥 Получен файл: {document.file_name}\n"
            f"📦 Размер: {document.file_size / 1024:.1f} KB\n\n"
            "⏳ Загружаю в GCS..."
        )
        
        # Генерируем уникальный ID
        job_id = str(uuid.uuid4())
        chat_id = update.effective_chat.id
        
        # Скачиваем файл из Telegram
        file = await context.bot.get_file(document.file_id)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dwg') as temp_file:
            await file.download_to_drive(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Загружаем в GCS
            storage_client = storage.Client()
            bucket = storage_client.bucket(GCS_BUCKET)
            
            gcs_path = f"raw/{chat_id}/{job_id}/{document.file_name}"
            blob = bucket.blob(gcs_path)
            blob.upload_from_filename(temp_path)
            
            file_url = f"gs://{GCS_BUCKET}/{gcs_path}"
            
            logger.info(f"✅ File uploaded to GCS: {file_url}")
            
            await update.message.reply_text(
                "✅ Файл загружен в GCS\n"
                "🚀 Отправляю на обработку в APS...\n\n"
                "⏱️ Это займет ~5-10 секунд"
            )
            
            # Отправляем на обработку
            result = processor_client.process_dwg(
                file_url=file_url,
                template="bti_template.dwg"
            )
            
            if result.get("status") == "success":
                output_url = result.get("output_url")
                workitem_id = result.get("workitem_id")
                stats = result.get("stats", {})
                
                success_message = (
                    "🎉 <b>Обработка завершена!</b>\n\n"
                    f"📎 Готовый файл: DWG с BTE шаблоном\n"
                    f"📊 Обработано: {stats.get('bytesDownloaded', 0)} bytes\n"
                    f"📤 Результат: {stats.get('bytesUploaded', 0)} bytes\n"
                    f"🆔 WorkItem: <code>{workitem_id[:20]}...</code>\n\n"
                    "📥 Скачиваю файл для отправки..."
                )
                
                await update.message.reply_text(success_message, parse_mode='HTML')
                
                # Скачиваем результат из GCS
                if output_url.startswith("gs://"):
                    output_gcs_path = output_url.replace("gs://", "").split("/", 1)
                    output_bucket = storage_client.bucket(output_gcs_path[0])
                    output_blob = output_bucket.blob(output_gcs_path[1])
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.dwg') as result_file:
                        output_blob.download_to_filename(result_file.name)
                        result_path = result_file.name
                    
                    try:
                        # Отправляем пользователю
                        with open(result_path, 'rb') as f:
                            await update.message.reply_document(
                                document=f,
                                filename=f"BTI_{document.file_name}",
                                caption="✅ Готовый DWG файл с BTE шаблоном"
                            )
                    finally:
                        os.unlink(result_path)
                
            else:
                error_message = (
                    "❌ <b>Ошибка обработки</b>\n\n"
                    f"Причина: {result.get('message', 'Unknown error')}\n\n"
                    "Попробуйте еще раз или обратитесь к администратору."
                )
                await update.message.reply_text(error_message, parse_mode='HTML')
        
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        logger.exception(f"❌ Error handling document: {e}")
        await update.message.reply_text(
            f"❌ Произошла ошибка при обработке файла.\n"
            f"Попробуйте еще раз или обратитесь к администратору."
        )


def create_application(token):
    """Создает Telegram Application"""
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    return application

