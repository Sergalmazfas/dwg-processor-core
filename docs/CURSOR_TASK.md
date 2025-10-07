# 🧭 CURSOR_TASK.md — Branch for BTE Activity Integration

**Ветка:** `feature/bte-activity`  
**Базовая ветка:** `main`  
**Статус:** 🔄 В разработке

---

## 🎯 Цель

Создать кастомную APS Activity, которая:
1. Открывает входной DWG
2. Вставляет BTE шаблон (INSERT command)
3. Сохраняет результат как DWG
4. Возвращает DWG (не PDF!)

**Это позволит** получать реальный DWG→DWG workflow с примененным BTE шаблоном.

---

## ⚙️ Основные шаги

### ✅ 1. Создать новую ветку (выполнено)

```bash
git checkout main
git pull
git checkout -b feature/bte-activity
```

**Статус:** ✅ Ветка создана

---

### ✅ 2. Добавить новую Activity для Autodesk APS (выполнено)

**Файл:** `aps_activity.json`

```json
{
  "id": "BTEInsertTemplate",
  "commandLine": [
    "$(engine.path)\\accoreconsole.exe /i \"$(args[HostDWG].path)\" /s \"$(settings[script].path)\" /isolate"
  ],
  "parameters": {
    "HostDWG": { "verb": "get", "localName": "input.dwg" },
    "BteTemplate": { "verb": "get", "localName": "bti_template.dwg" },
    "ResultDWG": { "verb": "put", "localName": "output.dwg" }
  },
  "settings": {
    "script": {
      "value": "INSERT bti_template.dwg 0,0 1 1 0\nQSAVE\nQUIT\n"
    }
  },
  "engine": "Autodesk.AutoCAD+25_0",
  "appbundles": [],
  "description": "Inserts BTE template into a DWG file"
}
```

**Статус:** ✅ Создан

---

### 🔄 3. Зарегистрировать Activity через APS API

**Опция A: Через Python скрипт** (рекомендуется)

```bash
python register_bte_activity.py
```

**Что делает:**
1. Получает Access Token
2. Отправляет POST /activities с данными из `aps_activity.json`
3. Создает alias `prod` для Activity
4. Выводит итоговый ID: `{client_id}.BTEInsertTemplate+prod`

**Опция B: Через Postman**

1. Импортировать коллекцию из `postman/`
2. Выполнить "Get Forge Token"
3. Создать новый запрос:
   - Method: POST
   - URL: `https://developer.api.autodesk.com/da/us-east/v3/activities`
   - Headers: `Authorization: Bearer {{forge_token}}`
   - Body: содержимое `aps_activity.json`

**Статус:** ⏳ TODO

---

### ✅ 4. Обновить APS клиент (выполнено)

**Файл:** `aps_client.py`

Добавлен параметр `use_bte_activity=False`:

```python
def submit_workitem_with_template(self, input_dwg_url, template_url, output_dwg_url, use_bte_activity=False):
    if use_bte_activity:
        # Используем BTEInsertTemplate Activity
        body = {
            "activityId": f"{self.client_id}.BTEInsertTemplate+prod",
            "arguments": {
                "HostDWG": {"url": input_dwg_url, "verb": "get"},
                "BteTemplate": {"url": template_url, "verb": "get"},
                "ResultDWG": {"url": output_dwg_url, "verb": "put"}
            }
        }
    else:
        # Стандартная Activity (fallback)
        body = {
            "activityId": "AutoCAD.PlotToPDF+25_0",
            ...
        }
```

**Статус:** ✅ Обновлен

---

### ✅ 5. Создать тест (выполнено)

**Файл:** `test_bte_activity.py`

```bash
python test_bte_activity.py
```

**Что проверяет:**
1. ✅ Access Token
2. ✅ Создание signed URLs
3. ✅ Отправка WorkItem с BTE Activity
4. ✅ Ожидание завершения
5. ✅ Проверка размера результата (должен быть > 10 KB если шаблон вставился)

**Статус:** ✅ Создан

---

### 🔄 6. Проверить результат WorkItem

После запуска `test_bte_activity.py`:

```bash
# Скачать отчет из логов
curl -s "<reportUrl>" | head -50

# Проверить что команды выполнились:
# - INSERT bti_template.dwg 0,0 1 1 0
# - QSAVE
# - QUIT

# Проверить размер выходного файла
gcloud storage ls -l gs://btibot-processed/test_bte_activity/result_with_template.dwg
```

**Ожидается:**
- ✅ Размер > 10 KB (шаблон вставлен)
- ✅ Команды INSERT, QSAVE, QUIT выполнены без ошибок
- ✅ Файл валидный DWG (можно открыть в AutoCAD)

**Статус:** ⏳ TODO

---

### 🔄 7. Создать коммит и пуш

```bash
git add .
git commit -m "✨ Add custom AutoCAD.BTEInsertTemplate Activity

Features:
- Custom Activity for DWG→DWG with BTE template insertion
- Activity definition in aps_activity.json
- Registration script: register_bte_activity.py
- Test script: test_bte_activity.py
- Updated aps_client.py with use_bte_activity parameter
- Fallback to standard Activity if BTE not available

Commands:
1. Register: python register_bte_activity.py
2. Test: python test_bte_activity.py"

git push origin feature/bte-activity
```

**Статус:** ⏳ TODO

---

## 🧱 Результат

После выполнения всех шагов:

### **🧩 Новая ветка:**
```
feature/bte-activity
├── aps_activity.json           # Определение Activity
├── register_bte_activity.py    # Скрипт регистрации
├── test_bte_activity.py        # Тест Activity
├── aps_client.py               # Обновлен (use_bte_activity)
└── docs/CURSOR_TASK.md         # Этот документ
```

### **⚙️ Рабочая Activity:**
```
ID: {client_id}.BTEInsertTemplate+prod
Engine: Autodesk.AutoCAD+25_0
Inputs: HostDWG, BteTemplate
Output: ResultDWG (DWG с вставленным шаблоном)
```

### **✅ DWG файл:**
```
Входной: Plan.dwg (15 KB)
Шаблон: bti_template.dwg
Результат: result_with_template.dwg (> 10 KB)
```

### **🔁 Возможность отката:**
```bash
# В любой момент можно вернуться к стабильной версии:
git checkout main
```

---

## 💬 Примечания

### **Что НЕ делаем:**
- ❌ Никаких PDF конвертаций
- ❌ Никаких Telegram зависимостей
- ❌ Только DWG → APS → DWG

### **Что делаем:**
- ✅ Регистрируем Activity через APS API
- ✅ Тестируем через Python / Postman
- ✅ Проверяем что шаблон реально вставляется
- ✅ Проверяем что результат - валидный DWG

### **После подтверждения:**
```bash
# Если всё работает - объединяем с main:
git checkout main
git merge feature/bte-activity
git push origin main
```

---

## 📋 Checklist

- [x] ✅ Ветка feature/bte-activity создана
- [x] ✅ aps_activity.json создан
- [x] ✅ register_bte_activity.py создан
- [x] ✅ test_bte_activity.py создан
- [x] ✅ aps_client.py обновлен
- [ ] ⏳ Activity зарегистрирована в APS
- [ ] ⏳ Тест выполнен успешно
- [ ] ⏳ Результат проверен (размер > 10 KB)
- [ ] ⏳ Код запушен на GitHub

---

## 🚀 Команды для выполнения

```bash
# 1. Зарегистрировать Activity
python register_bte_activity.py

# 2. Запустить тест
python test_bte_activity.py

# 3. Проверить результат
gcloud storage ls -l gs://btibot-processed/test_bte_activity/

# 4. Закоммитить
git add .
git commit -m "✨ Add BTE Activity integration"
git push origin feature/bte-activity
```

**Готово к выполнению! 🎯**

