# 🧩 BTE AppBundle для Autodesk APS

**Официальная документация:** https://aps.autodesk.com/en/docs/design-automation/v3/  
**Пример:** https://github.com/autodesk-platform-services/aps-tutorial-postman/tree/master/DA4ACAD

---

## 📦 Что такое AppBundle

AppBundle - это ZIP архив с .NET плагином для AutoCAD, который:
- Загружается в Autodesk APS
- Выполняется в AutoCAD Core Engine на серверах Autodesk
- Может выполнять кастомные команды (например, INSERTBTE)

---

## 📁 Структура (согласно официальному формату)

```
bte-appbundle/
├── PackageContents.xml          # Обязательно! Описание плагина
├── Contents/
│   └── Windows/
│       └── InsertTemplate.dll   # Скомпилированный .NET плагин
├── package.json                 # Метаданные для APS
├── InsertTemplate.cs            # Исходный код C#
└── scripts/
    ├── register_appbundle.sh    # Регистрация AppBundle
    ├── register_activity.sh     # Создание Activity
    └── test_workitem.sh         # Тест WorkItem
```

---

## 🚀 АВТОМАТИЧЕСКАЯ СБОРКА DLL (БЕЗ AUTOCAD!)

### **🔧 Быстрая сборка с PowerShell:**

**Шаг 1: Запустить автоматический скрипт**
```powershell
# На Windows с PowerShell:
pwsh build_dll.ps1

# На macOS/Linux с PowerShell Core:
pwsh build_dll.ps1
```

**Что делает скрипт:**
1. ✅ Скачивает AutoCAD SDK DLLs с GitHub
2. ✅ Компилирует InsertTemplate.cs → InsertTemplate.dll
3. ✅ Создает ZIP архив InsertTemplateAppBundle.zip
4. ✅ Готов к регистрации в APS!

**Результат:**
```
✅ SDK DLLs downloaded
✅ InsertTemplate.dll compiled (XX KB)
✅ AppBundle ZIP created (XX KB)
```

### **Альтернативные опции:**

**Опция 1: Автоматический скрипт (рекомендуется) ⭐**
```bash
pwsh build_dll.ps1
```

**Опция 2: Компиляция вручную на Windows**
```bash
csc /target:library /out:Contents/Windows/InsertTemplate.dll InsertTemplate.cs \
    /r:"C:\Program Files\Autodesk\AutoCAD 2025\acdbmgd.dll" \
    /r:"C:\Program Files\Autodesk\AutoCAD 2025\acmgd.dll"
```

**Опция 3: Использовать pre-compiled DLL**
```bash
# Если DLL уже есть, просто положить в Contents/Windows/
```

---

## 🚀 Регистрация в APS (после компиляции DLL)

**После успешной сборки через `build_dll.ps1` выполните:**

### **Шаг 1: Зарегистрировать AppBundle**
```bash
cd scripts
python register_appbundle.py
```
**Что происходит:**
- ✅ POST /appbundles - создается AppBundle в APS
- ✅ Получаем uploadParameters (S3 URL)

### **Шаг 2: Загрузить ZIP на S3**
```bash
python upload_appbundle.py
```
**Что происходит:**
- ✅ ZIP загружается на S3 сервера Autodesk
- ✅ AppBundle доступен для Activities

### **Шаг 3: Создать Activity с AppBundle**
```bash
python register_activity.py
```
**Что происходит:**
- ✅ POST /activities - создается Activity
- ✅ Activity использует ваш AppBundle
- ✅ Команда INSERTBTE готова к выполнению

### **Шаг 4: Протестировать WorkItem**
```bash
python test_workitem.py
```
**Что происходит:**
- ✅ POST /workitems - запускается обработка
- ✅ DWG обрабатывается на серверах Autodesk
- ✅ INSERTBTE выполняется на C:\DARoot\ (Windows)

### **Шаг 5: Проверить отчет**
```bash
bash verify_report.sh
```
**Что происходит:**
- ✅ Скачивается report.log от Autodesk
- ✅ Проверяется наличие команд INSERTBTE, QSAVE, QUIT
- ✅ Подтверждается успешное выполнение

---

## ✅ Ожидаемый результат

### **В отчете от Autodesk должно быть:**
```
[Date Time] Loading AppBundle: InsertTemplateAppBundle
[Date Time] AppBundle loaded successfully
[Date Time] Command: INSERTBTE
[Date Time] 🔸 Starting BTE template insertion...
[Date Time] 🔸 Processing DWG with BTE logic...
[Date Time] ✅ BTE template processing complete
[Date Time] ✅ File saved as output.dwg
[Date Time] Command: QSAVE
[Date Time] Command: QUIT
```

---

## 📋 Текущий статус

- [x] ✅ Структура создана
- [x] ✅ InsertTemplate.cs написан
- [x] ✅ PackageContents.xml создан (официальный формат)
- [x] ✅ package.json создан
- [ ] ⏳ InsertTemplate.dll - требует компиляции
- [ ] ⏳ ZIP архив - после DLL
- [ ] ⏳ Регистрация в APS - после ZIP

---

## 🔧 Альтернатива (для быстрого теста)

**Если компиляция DLL затруднительна:**

Можно использовать script-based подход (без DLL):
```json
{
  "settings": {
    "script": {
      "value": "INSERT bti_template.dwg 0,0 1 1 0\nQSAVE\nQUIT\n"
    }
  }
}
```

Но это уже пробовали - работает не полностью из-за проблемы с alias.

**Рекомендация:** Найти способ скомпилировать DLL или использовать готовый.

