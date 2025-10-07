# 📮 Postman Collection для DWG Processor Core

## 📥 Импорт в Postman

### **Шаг 1: Импортировать коллекцию**

1. Откройте Postman
2. **Import** → **File**
3. Выберите `DWG_Processor_Core.postman_collection.json`
4. **Import**

### **Шаг 2: Импортировать environment**

1. **Environments** → **Import**
2. Выберите `DWG_Processor_Core.postman_environment.json`
3. **Import**

### **Шаг 3: Настроить credentials**

В Environment установите:
- `forge_client_id` - ваш Forge Client ID
- `forge_client_secret` - ваш Forge Client Secret

Остальные переменные автоматически заполнятся при выполнении запросов.

---

## 🧪 Тестирование

### **Test Suite 1: Core Service Tests**

#### **1.1. Health Check - Core**
```
GET /health
```

**Ожидаемый результат:**
```json
{
  "status": "ok",
  "service": "dwg-processor-core"
}
```

**✅ Успех:** Status 200, сервис работает

---

#### **1.2. Process DWG - Core API**
```
POST /process-dwg
```

**Request Body:**
```json
{
  "file_url": "gs://btibot-processed/raw/1759837370/Plan 2025-10-03 155019_export_2D_room_height.dwg",
  "template": "bti_template.dwg"
}
```

**Ожидаемый результат:**
```json
{
  "status": "success",
  "workitem_id": "abc123...",
  "output_url": "gs://btibot-processed/processed/dwg/{job_id}/result.dwg",
  "job_id": "uuid...",
  "stats": {
    "bytesDownloaded": 15046,
    "bytesUploaded": 12983
  }
}
```

**✅ Успех:** Status 200, DWG обработан через APS

---

### **Test Suite 2: Telegram Bot Tests**

#### **2.1. Health Check - Bot**
```
GET /health
```

**Ожидаемый результат:**
```json
{
  "status": "ok",
  "service": "telegram-bti-bot"
}
```

**✅ Успех:** Status 200, бот работает

---

#### **2.2. Set Webhook**
```
POST /set-webhook
```

**Ожидаемый результат:**
```json
{
  "status": "success",
  "webhook_url": "https://telegram-bti-bot-637190449180.europe-west1.run.app/webhook",
  "telegram_response": {
    "ok": true,
    "result": true,
    "description": "Webhook was set"
  }
}
```

**✅ Успех:** Webhook установлен для Telegram

---

### **Test Suite 3: Full Pipeline Test**

Этот набор тестирует полный цикл работы с Autodesk Forge API:

#### **3.1. Get Forge Token**
```
POST https://developer.api.autodesk.com/authentication/v2/token
```

**Автоматически сохраняет токен в переменную `forge_token`**

**✅ Успех:** Получен access_token на 3600 секунд

---

#### **3.2. List Activities**
```
GET /da/us-east/v3/activities
```

**Показывает доступные Activities**, включая:
- Autodesk.AutoCAD+24
- BotBti.SimpleDWG2DWG_NoTemplate (если создана)

**✅ Успех:** Список Activities получен

---

#### **3.3. Process DWG (Full Pipeline)**
```
POST /process-dwg
```

**Полный цикл:**
1. Получает DWG из GCS
2. Создает signed URLs
3. Отправляет в Autodesk APS
4. Применяет BTE шаблон
5. Сохраняет результат в GCS

**Автоматически сохраняет:**
- `workitem_id` - ID WorkItem в APS
- `output_url` - URL результата в GCS

**✅ Успех:** Status 200, файл обработан

---

## 📋 Порядок тестирования

### **Быстрый тест (1-2 минуты):**
```
1. Health Check - Core       ✅
2. Health Check - Bot         ✅
3. Process DWG - Core API     ✅ (5-10 секунд)
```

### **Полный тест (3-5 минут):**
```
1. Get Forge Token            ✅
2. List Activities            ✅
3. Health Check - Core        ✅
4. Health Check - Bot         ✅
5. Set Webhook                ✅
6. Process DWG (Full)         ✅ (ждет завершения WorkItem)
```

---

## 🔧 Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `core_url` | URL dwg-processor-core | https://dwg-processor-core-... |
| `bot_url` | URL telegram-bti-bot | https://telegram-bti-bot-... |
| `forge_client_id` | Forge Client ID | m6CK3EH... |
| `forge_client_secret` | Forge Client Secret | SECRET |
| `forge_token` | Access Token (авто) | eyJhbG... |
| `workitem_id` | WorkItem ID (авто) | abc123... |
| `output_url` | Result URL (авто) | gs://... |
| `test_file_url` | Тестовый DWG | gs://btibot-processed/... |

---

## ✅ Ожидаемые результаты

### **Все тесты должны вернуть 200 OK:**

```
✅ Health Check - Core          → 200 OK
✅ Health Check - Bot            → 200 OK
✅ Set Webhook                   → 200 OK
✅ Get Forge Token               → 200 OK
✅ List Activities               → 200 OK
✅ Process DWG - Core API        → 200 OK (5-10 сек)
```

### **После теста "Process DWG":**

Проверьте в GCS:
```bash
gcloud storage ls gs://btibot-processed/processed/dwg/
```

Должен появиться новый файл `result.dwg`

---

## 🎯 Troubleshooting

### **❌ Health check failed**
**Проблема:** Сервис не запущен  
**Решение:** Проверьте Cloud Run логи

### **❌ 401 Unauthorized (Forge Token)**
**Проблема:** Неправильные credentials  
**Решение:** Обновите `forge_client_id` и `forge_client_secret`

### **❌ 400 Bad Request (Process DWG)**
**Проблема:** Неправильный file_url или Activity  
**Решение:** Проверьте что файл существует в GCS

### **❌ Webhook not set**
**Проблема:** BOT_TOKEN не настроен  
**Решение:** Проверьте Secret Manager

---

## 📚 Ссылки

- [Postman Documentation](https://learning.postman.com/docs/)
- [Autodesk APS API](https://aps.autodesk.com/en/docs/design-automation/v3)
- [dwg-processor-core Service](https://dwg-processor-core-637190449180.europe-west1.run.app/health)
- [telegram-bti-bot Service](https://telegram-bti-bot-637190449180.europe-west1.run.app/health)

---

## 🎉 Готово!

Импортируйте коллекцию в Postman и запустите тесты! 🚀

