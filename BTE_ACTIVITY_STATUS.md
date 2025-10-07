# 📋 BTE Activity Integration - Status Report

**Дата:** 2025-10-07  
**Ветка:** `feature/bte-activity`  
**Статус:** ⚠️ ЧАСТИЧНО ВЫПОЛНЕНО

---

## ✅ Что сделано

### **1. Activity создана** ✅
```
ID: BotBti.BTEInsertTemplate
Version: 1
Status: Registered in APS
```

### **2. Файлы созданы** ✅
- ✅ `aps_activity.json` - определение Activity
- ✅ `register_bte_activity.py` - скрипт регистрации
- ✅ `test_bte_activity.py` - тест Activity
- ✅ `aps_client.py` - обновлен (use_bte_activity параметр)
- ✅ `docs/CURSOR_TASK.md` - техническое задание

---

## ⚠️ Проблема с alias

### **Ошибка:**
```
POST /activities/BotBti.BTEInsertTemplate/aliases
Response: {"id": ["Cannot parse id."]}
```

### **Что пробовали:**
- ❌ Создать alias `prod`
- ❌ Создать alias `v1`
- ✅ Activity зарегистрирована как `BotBti.BTEInsertTemplate+$LATEST`

### **Проблема:**
APS не позволяет использовать `$LATEST` в WorkItem:
```
Error: Cannot use the alias $LATEST as a reference
```

---

## 🔧 Решение (Fallback)

### **Текущая реализация:**

В `aps_client.py` используется **fallback стратегия:**

```python
def submit_workitem_with_template(..., use_bte_activity=False):
    if use_bte_activity:
        # Пытаемся использовать BTE Activity
        activity_id = "BotBti.BTEInsertTemplate+1"
    else:
        # Fallback на стандартную Activity (работает всегда)
        activity_id = "AutoCAD.PlotToPDF+25_0"
```

**По умолчанию: `use_bte_activity=False`**  
→ Используется стандартная Activity `AutoCAD.PlotToPDF+25_0` (✅ протестировано, работает)

---

## 📊 Текущая работоспособность

### **Production (работает):**
```bash
# Через dwg-processor-core (без BTE Activity)
curl -X POST https://dwg-processor-core-637190449180.europe-west1.run.app/process-dwg \
  -d '{"file_url":"gs://btibot-processed/raw/test.dwg","template":"bti_template.dwg"}'

✅ Использует: AutoCAD.PlotToPDF+25_0
✅ Результат: PDF (работает)
✅ Время: ~5-10 секунд
```

### **BTE Activity (не работает):**
```bash
# С use_bte_activity=True
python test_bte_activity.py

❌ Activity not found: BotBti.BTEInsertTemplate+1
❌ Cannot use $LATEST alias
```

---

## 🎯 Следующие шаги

### **Опция 1: Исправить alias (рекомендуется)**

**Проблема:** APS не принимает создание alias через API

**Решение:**
1. Проверить официальную документацию APS по созданию alias
2. Возможно нужно использовать другой endpoint
3. Или создавать alias через Postman UI

**Ресурсы:**
- https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/activities-id-aliases-POST/
- https://github.com/autodesk-platform-services/aps-tutorial-postman

---

### **Опция 2: Использовать AppBundle (альтернатива)**

Вместо script-based Activity создать AppBundle с .NET плагином:

```csharp
// BTI_TemplatePlugin.cs
public class BTIPlugin : IExtensionApplication
{
    public void Initialize()
    {
        // INSERT template logic
    }
}
```

**Преимущества:**
- ✅ Больше контроля
- ✅ Сложная логика обработки
- ✅ Можно использовать AutoCAD .NET API

**Недостатки:**
- ⏱️ Требует компиляции .NET DLL
- 🔧 Сложнее в поддержке

---

### **Опция 3: Оставить текущее решение (быстро)**

**Что работает сейчас:**
```
✅ AutoCAD.PlotToPDF+25_0
✅ Обработка DWG → PDF
✅ Полный цикл работает
✅ Telegram бот работает
```

**Что не работает:**
```
❌ BTE Activity alias
❌ DWG→DWG с шаблоном (пока)
```

---

## ✅ Рекомендация

### **Для production сейчас:**

Использовать стандартную Activity (уже работает):
```python
# В app.py / aps_client.py
use_bte_activity=False  # Default - работает!
```

### **Для разработки BTE:**

1. Изучить официальную документацию по alias
2. Попробовать создать alias через Postman UI
3. Или перейти на AppBundle подход

---

## 📁 Что в ветке feature/bte-activity

```
✅ aps_activity.json              - Определение Activity
✅ register_bte_activity.py        - Регистрация (работает частично)
✅ test_bte_activity.py            - Тест (не работает без alias)
✅ aps_client.py                   - Обновлен (fallback работает)
✅ docs/CURSOR_TASK.md             - Техническое задание
```

**Ветка готова к merge в main** с текущим fallback решением.

---

## 🎉 Итог

```
┌────────────────────────────────────────────┐
│  ✅ Система работает в production          │
│  ✅ Fallback на AutoCAD.PlotToPDF+25_0     │
│  ⚠️ BTE Activity создана но alias не работает │
│  📚 Документация готова                    │
│  🚀 Готово к merge в main                  │
└────────────────────────────────────────────┘
```

**Можно использовать в production с fallback!** 🚀

