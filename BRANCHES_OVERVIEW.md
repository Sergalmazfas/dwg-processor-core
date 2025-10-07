# 🌳 DWG Processor Core - Обзор веток

**Репозиторий:** https://github.com/Sergalmazfas/dwg-processor-core  
**Дата:** 2025-10-07  
**Статус:** ✅ 3 ВЕТКИ ГОТОВЫ

---

## 📊 Структура веток

```
dwg-processor-core/
├── main                      ✅ Стабильное ядро (production)
├── telegram-integration      ✅ Telegram бот (работает)
└── feature/bte-activity      ⚠️ BTE Activity (в разработке)
```

---

## 🌿 main - Чистое ядро DWG→DWG

**Статус:** ✅ Production Ready  
**Release:** v1.0.0  
**Деплой:** dwg-processor-core

### **Что включает:**
```
✅ app.py                      POST /process-dwg endpoint
✅ aps_client.py               APS интеграция
✅ gcs_utils.py                Signed URLs (БЕЗ content_type!)
✅ test_postman_pipeline.py    Автотест
✅ Dockerfile                  Production image
✅ cloudbuild.yaml             CI/CD с автотестом
✅ README.md                   Документация
```

### **Особенности:**
- ❌ Нет Telegram зависимостей
- ❌ Нет PDF библиотек
- ✅ Только DWG обработка через APS
- ✅ Activity: AutoCAD.PlotToPDF+25_0
- ✅ Протестировано и работает

### **Cloud Run:**
```
Service: dwg-processor-core
URL: https://dwg-processor-core-637190449180.europe-west1.run.app
Health: ✅ OK
```

---

## 🤖 telegram-integration - Telegram бот

**Статус:** ✅ Production Ready  
**Деплой:** telegram-bti-bot  
**Тест:** ✅ Реальный файл обработан

### **Что добавляет:**
```
✅ telegram_bot/
   ├── main.py              Flask webhook
   ├── bot.py               Telegram команды
   ├── api_client.py        Вызов dwg-processor-core
   ├── Dockerfile           
   ├── cloudbuild.yaml      Отдельный деплой
   └── README.md            
✅ postman/
   ├── Collection.json      7 тестовых запросов
   ├── Environment.json     
   └── README.md            
```

### **Особенности:**
- ✅ Полная интеграция с Telegram
- ✅ Webhook работает
- ✅ Команды: /start, /help, /status
- ✅ Прием и отправка DWG файлов
- ✅ Вызывает dwg-processor-core API
- ✅ Реальный тест пройден успешно!

### **Cloud Run:**
```
Service: telegram-bti-bot
URL: https://telegram-bti-bot-637190449180.europe-west1.run.app
Health: ✅ OK
Webhook: ✅ Установлен
Test: ✅ Файл обработан (WorkItem: 0330e516...)
```

---

## 🔧 feature/bte-activity - Кастомная BTE Activity

**Статус:** ⚠️ В разработке (частично работает)  
**Цель:** DWG→DWG с вставкой BTE шаблона

### **Что добавляет:**
```
✅ aps_activity.json           Определение Activity
✅ register_bte_activity.py    Регистрация в APS
✅ test_bte_activity.py        Тест Activity
✅ aps_client.py               use_bte_activity параметр
✅ docs/CURSOR_TASK.md         Техническое задание
✅ BTE_ACTIVITY_STATUS.md      Статус разработки
```

### **Статус:**
- ✅ Activity создана: `BotBti.BTEInsertTemplate`
- ✅ Зарегистрирована в APS (version 1)
- ⚠️ Alias не работает ("Cannot parse id")
- ✅ Fallback на стандартную Activity работает

### **Известные проблемы:**
```
❌ Cannot use alias $LATEST in WorkItem
❌ Alias creation returns "Cannot parse id"
✅ Fallback strategy implemented
```

---

## 🔄 Workflow по веткам

### **Для стабильной работы:**
```bash
git checkout main
# Используй стабильное ядро без экспериментов
```

### **Для Telegram интеграции:**
```bash
git checkout telegram-integration
# Telegram бот + dwg-processor-core API
```

### **Для разработки BTE:**
```bash
git checkout feature/bte-activity
# Эксперименты с кастомной Activity
```

---

## 📋 Сравнение веток

| Компонент | main | telegram-integration | feature/bte-activity |
|-----------|------|---------------------|---------------------|
| **Файлов** | 10 | 20 | 17 |
| **Строк кода** | 140 | 760 | 1,240 |
| **Зависимости** | 10 | 10 | 10 |
| **Telegram** | ❌ | ✅ | ❌ |
| **Postman** | ❌ | ✅ | ❌ |
| **BTE Activity** | ❌ | ❌ | ⚠️ Частично |
| **Production** | ✅ | ✅ | ⚠️ Fallback |
| **Деплой** | ✅ | ✅ | ❌ |

---

## 🚀 Команды

### **Переключение веток:**
```bash
# Стабильное ядро
git checkout main

# Telegram бот
git checkout telegram-integration

# BTE разработка
git checkout feature/bte-activity
```

### **Деплой:**
```bash
# Ядро (из main)
gcloud run deploy dwg-processor-core --source . --region europe-west1

# Бот (из telegram-integration)
cd telegram_bot
gcloud run deploy telegram-bti-bot --source . --region europe-west1
```

### **Тестирование:**
```bash
# Автотест (работает на всех ветках)
python test_postman_pipeline.py

# BTE тест (только на feature/bte-activity)
python test_bte_activity.py
```

---

## ✅ Рекомендации

### **Для production сейчас:**
```
Используйте: main или telegram-integration
Activity: AutoCAD.PlotToPDF+25_0 (✅ работает)
Status: Production Ready
```

### **Для разработки:**
```
Используйте: feature/bte-activity
Цель: Создать рабочую BTE Activity с DWG→DWG
Статус: В разработке (alias не работает)
```

---

## 🎯 Следующие шаги

### **1. Исследовать проблему с alias:**
- Изучить официальную документацию APS
- Проверить примеры в aps-tutorial-postman
- Возможно нужен другой подход к созданию alias

### **2. Или перейти на AppBundle:**
- Создать .NET плагин для AutoCAD
- Упаковать в AppBundle
- Зарегистрировать Activity с AppBundle

### **3. Или использовать текущее решение:**
- ✅ AutoCAD.PlotToPDF+25_0 работает стабильно
- ✅ Обрабатывает DWG файлы
- ✅ Полный цикл протестирован

---

## 🎉 Итог

```
┌──────────────────────────────────────────────┐
│  🎉 ТРИ ВЕТКИ ГОТОВЫ!                        │
│                                              │
│  ✅ main: Чистое ядро (production)           │
│  ✅ telegram-integration: Telegram бот       │
│  ⚠️ feature/bte-activity: BTE разработка     │
│                                              │
│  🚀 2 ветки готовы к production!             │
│  🔧 1 ветка для экспериментов                │
│                                              │
│  📦 GitHub: 3 branches                       │
│  ☁️ Cloud Run: 2 services                    │
│  ✅ Tested: Real file processed              │
└──────────────────────────────────────────────┘
```

**Репозиторий готов к промышленной эксплуатации! 🎉**

