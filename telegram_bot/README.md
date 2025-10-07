# 🤖 Telegram BTI Bot

> Telegram интеграция для dwg-processor-core

## 🎯 Назначение

Telegram бот для обработки DWG файлов с применением BTE шаблона.

**Архитектура:**
```
Telegram User → Bot → GCS → dwg-processor-core → APS → Result → User
```

## 📋 Команды

- `/start` - Главное меню
- `/help` - Справка
- `/status` - Проверить статус сервиса

## 📤 Использование

1. Отправьте DWG файл боту
2. Бот загружает в GCS
3. Отправляет на обработку в `dwg-processor-core`
4. Получает результат с применением BTE шаблона
5. Отправляет готовый DWG обратно

## 🚀 Деплой

```bash
# Из корня репозитория
gcloud builds submit --config telegram_bot/cloudbuild.yaml --project talkhint
```

Или напрямую:

```bash
cd telegram_bot

gcloud run deploy telegram-bti-bot \
  --source . \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="GCS_BUCKET=btibot-processed,DWG_PROCESSOR_URL=https://dwg-processor-core-637190449180.europe-west1.run.app" \
  --set-secrets="BOT_TOKEN=BOT_TOKEN:latest" \
  --service-account="637190449180-compute@developer.gserviceaccount.com"
```

## 🔧 Настройка webhook

После деплоя:

```bash
curl -X POST https://telegram-bti-bot-637190449180.europe-west1.run.app/set-webhook
```

Или вручную:

```bash
curl -X POST https://api.telegram.org/bot<BOT_TOKEN>/setWebhook \
  -d "url=https://telegram-bti-bot-637190449180.europe-west1.run.app/webhook"
```

## 📊 Переменные окружения

**Обязательные:**
- `BOT_TOKEN` - Telegram Bot Token (из Secret Manager)

**Опциональные:**
- `GCS_BUCKET` - GCS bucket для файлов (default: btibot-processed)
- `DWG_PROCESSOR_URL` - URL dwg-processor-core (default: https://dwg-processor-core-637190449180.europe-west1.run.app)

## 🏗️ Архитектура

```
┌─────────────┐
│  Telegram   │
│    User     │
└──────┬──────┘
       │ 1. Upload DWG
       ▼
┌─────────────────────────────┐
│  telegram-bti-bot           │
│  (Flask + python-telegram-bot)│
│                             │
│  /webhook                   │
│  ├─ Получить файл           │
│  ├─ Загрузить в GCS         │
│  └─ Вызвать API             │
└──────┬──────────────────────┘
       │ 2. POST /process-dwg
       ▼
┌─────────────────────────────┐
│  dwg-processor-core         │
│                             │
│  ├─ Создать signed URLs     │
│  ├─ Отправить в APS         │
│  └─ Дождаться результата    │
└──────┬──────────────────────┘
       │ 3. WorkItem
       ▼
┌─────────────────────────────┐
│  Autodesk APS               │
│  Design Automation          │
│                             │
│  ├─ Open DWG                │
│  ├─ Apply BTE Template      │
│  └─ Save DWG                │
└──────┬──────────────────────┘
       │ 4. Upload result
       ▼
┌─────────────────────────────┐
│  Google Cloud Storage       │
│  gs://btibot-processed/     │
│                             │
│  ready/.../result.dwg       │
└──────┬──────────────────────┘
       │ 5. Download & Send
       ▼
┌─────────────┐
│  Telegram   │
│    User     │
└─────────────┘
```

## 📝 Файлы

- `main.py` - Flask приложение с webhook
- `bot.py` - Логика команд и обработки файлов
- `api_client.py` - Клиент для dwg-processor-core
- `requirements.txt` - Зависимости
- `Dockerfile` - Docker образ
- `cloudbuild.yaml` - CI/CD конфигурация

## ✅ Готово!

Telegram интеграция готова к деплою! 🎉

