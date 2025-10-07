# 🏗️ DWG Processor Core

> Чистая DWG→DWG обработка через Autodesk APS с применением BTE шаблона

## 🎯 Назначение

Микросервис для обработки DWG файлов:
- ✅ Только DWG (без PDF конвертации)
- ✅ Применение BTE шаблона через Autodesk APS
- ✅ Чистый код без Telegram и других зависимостей
- ✅ Production-ready с автоматическим тестированием

## 📋 API

### POST /process-dwg

Обрабатывает DWG файл через APS с применением BTE шаблона.

**Request:**
```json
{
  "file_url": "gs://btibot-queue/test_input.dwg",
  "template": "bti_template.dwg"
}
```

**Response:**
```json
{
  "status": "success",
  "workitem_id": "abc123...",
  "output_url": "gs://btibot-processed/result_bti_2025.dwg",
  "job_id": "uuid...",
  "stats": {
    "bytesDownloaded": 15046,
    "bytesUploaded": 12983
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "dwg-processor-core"
}
```

## 🚀 Локальный запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервиса
python app.py
```

Сервис будет доступен на `http://localhost:8080`

## 🧪 Тестирование

Автоматический тест полного DWG→DWG pipeline:

```bash
python test_postman_pipeline.py
```

Тест выполняет:
1. ✅ Получение Access Token
2. ✅ Создание signed URLs
3. ✅ Загрузку DWG и шаблона
4. ✅ Создание WorkItem
5. ✅ Ожидание завершения
6. ✅ Проверку результата

## 📦 Деплой

### Cloud Build (автоматический)

```bash
gcloud builds submit --config cloudbuild.yaml --project talkhint
```

Cloud Build автоматически:
1. Запустит тест DWG pipeline
2. Соберет Docker образ
3. Задеплоит в Cloud Run (если тест пройден)

### Cloud Run (ручной)

```bash
gcloud run deploy dwg-processor-core \
  --source . \
  --project talkhint \
  --region europe-west1 \
  --allow-unauthenticated
```

## 🏗️ Архитектура

```
┌─────────────────────────────────────┐
│  POST /process-dwg                  │
│                                     │
│  1. Получает file_url + template   │
│  2. Создает signed URLs             │
│  3. Отправляет в APS                │
│  4. Ждет завершения                 │
│  5. Возвращает result URL           │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Autodesk APS                       │
│  Design Automation API              │
│                                     │
│  Activity: Autodesk.AutoCAD+25      │
│  - Загружает DWG                    │
│  - Применяет BTE шаблон             │
│  - Сохраняет результат              │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Google Cloud Storage               │
│  gs://btibot-processed/             │
│                                     │
│  processed/dwg/{job_id}/result.dwg  │
└─────────────────────────────────────┘
```

## 🔧 Компоненты

### app.py
Flask приложение с POST /process-dwg endpoint.

### aps_client.py
Клиент для работы с Autodesk APS:
- Получение Access Token
- Создание WorkItem с BTE шаблоном
- Проверка статуса
- Ожидание завершения

### gcs_utils.py
Утилиты для работы с GCS:
- Создание signed URLs (GET/PUT)
- Создание публичных URLs
- Upload/Download файлов

### test_postman_pipeline.py
Автоматический тест полного pipeline (аналог Postman коллекции).

## 📊 Метрики

- ⏱️ Среднее время обработки: ~3-5 секунд
- 📦 Размер Docker образа: ~200 MB
- 💾 Память: 2 Gi
- 🔄 CPU: 2
- 📈 Max instances: 10

## 🔐 Секреты

Требуемые секреты в Google Secret Manager:
- `FORGE_CLIENT_ID` - Autodesk APS Client ID
- `FORGE_CLIENT_SECRET` - Autodesk APS Client Secret
- `FORGE_SERVICE_KEY` - GCS Service Account Key

## 🔗 Ссылки

- [Autodesk APS Documentation](https://aps.autodesk.com/en/docs/design-automation/v3)
- [Google Cloud Run](https://cloud.google.com/run)
- [Service URL](https://dwg-processor-core-637190449180.europe-west1.run.app)

## 📝 License

MIT

---

**Готово к продакшену! 🚀**

