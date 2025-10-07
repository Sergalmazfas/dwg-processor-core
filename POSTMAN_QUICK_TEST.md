# 🚀 Быстрый тест через Postman

## 📥 Шаг 1: Импорт

1. Откройте Postman
2. **Import** → выберите оба файла из папки `postman/`:
   - `DWG_Processor_Core.postman_collection.json`
   - `DWG_Processor_Core.postman_environment.json`

3. Выберите Environment: **"DWG Processor Core - Environment"**

---

## 🔑 Шаг 2: Настройка credentials (опционально для Full Pipeline)

В Environment установите:
- `forge_client_id` - получите из Secret Manager
- `forge_client_secret` - получите из Secret Manager

```bash
# Получить credentials:
gcloud secrets versions access latest --secret=FORGE_CLIENT_ID --project=talkhint
gcloud secrets versions access latest --secret=FORGE_CLIENT_SECRET --project=talkhint
```

---

## ✅ Шаг 3: Запуск тестов

### **Вариант A: Быстрый тест (30 секунд)**

Выполните по порядку:

1. **Core Service Tests** → **Health Check - Core**
   - Ожидаем: `200 OK`, `{"status": "ok"}`
   
2. **Telegram Bot Tests** → **Health Check - Bot**
   - Ожидаем: `200 OK`, `{"status": "ok"}`
   
3. **Core Service Tests** → **Process DWG - Core API**
   - Ожидаем: `200 OK`, результат обработки DWG
   - Время: ~5-10 секунд

**✅ Если все 3 запроса вернули 200 - система работает!**

---

### **Вариант B: Полный тест (2-3 минуты)**

Выполните всю коллекцию по порядку:

1. **Full Pipeline Test** → **Get Forge Token**
   - Сохранит токен в `forge_token`
   
2. **Full Pipeline Test** → **List Activities**
   - Покажет доступные Activities
   
3. **Core Service Tests** → **Health Check - Core**
   
4. **Telegram Bot Tests** → **Health Check - Bot**
   
5. **Telegram Bot Tests** → **Set Webhook**
   
6. **Full Pipeline Test** → **Process DWG (Full Pipeline)**
   - Полный цикл DWG → APS → Result
   - Время: ~5-10 секунд

---

## 📊 Ожидаемые результаты

### **После "Process DWG - Core API":**

```json
{
  "status": "success",
  "workitem_id": "70110a7ddc8c451489a036c820333c40",
  "output_url": "gs://btibot-processed/processed/dwg/a1b2c3d4-e5f6/result.dwg",
  "job_id": "a1b2c3d4-e5f6-...",
  "stats": {
    "bytesDownloaded": 15046,
    "bytesUploaded": 12983
  }
}
```

### **Проверка результата в GCS:**

```bash
# Скопируйте output_url из ответа и проверьте:
gcloud storage ls gs://btibot-processed/processed/dwg/
```

Должен быть создан файл `result.dwg`

---

## 🎯 Быстрый чеклист

Выполните эти 3 запроса для быстрой проверки:

- [ ] Health Check - Core → 200 OK
- [ ] Health Check - Bot → 200 OK  
- [ ] Process DWG - Core API → 200 OK (результат через 5-10 сек)

**Если все ✅ - система полностью работает!** 🎉

---

## 🐛 Troubleshooting

### **❌ Health check failed (503/504)**
**Решение:** Подождите 30 секунд (cold start), повторите

### **❌ 401 Unauthorized (Forge Token)**
**Решение:** Проверьте `forge_client_id` и `forge_client_secret` в Environment

### **❌ 400 Bad Request (Process DWG)**
**Решение:** Проверьте что тестовый файл существует:
```bash
gcloud storage ls gs://btibot-processed/raw/1759837370/
```

### **❌ Timeout (процесс зависает)**
**Решение:** Увеличьте timeout в Postman: Settings → Request timeout → 120000ms

---

## 🎉 Готово!

Запустите тесты в Postman и убедитесь что система работает! 🚀

**GitHub:** https://github.com/Sergalmazfas/dwg-processor-core/tree/telegram-integration/postman

