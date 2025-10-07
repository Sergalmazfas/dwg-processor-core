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

## ⚠️ ВАЖНО: Компиляция DLL

### **Проблема:**
Для компиляции InsertTemplate.cs → InsertTemplate.dll нужен:
- Windows с установленным AutoCAD 2025
- Или Visual Studio с AutoCAD SDK

### **Решение для нашего случая:**

**Опция 1: Использовать pre-compiled DLL**
```bash
# Скачать готовый DLL из BTI_TemplateAppBundle (если есть)
# Или использовать простой DLL для теста
```

**Опция 2: Скомпилировать на Windows (локально)**
```bash
csc /target:library /out:Contents/Windows/InsertTemplate.dll InsertTemplate.cs \
    /r:"C:\Program Files\Autodesk\AutoCAD 2025\acdbmgd.dll" \
    /r:"C:\Program Files\Autodesk\AutoCAD 2025\acmgd.dll"
```

**Опция 3: Использовать GitHub Actions с Windows runner**
```yaml
runs-on: windows-latest
# Установить AutoCAD SDK
# Скомпилировать DLL
```

---

## 🚀 Регистрация в APS (после компиляции DLL)

### **Шаг 1: Создать ZIP**
```bash
cd bte-appbundle
zip -r InsertTemplateAppBundle.zip PackageContents.xml Contents package.json
```

### **Шаг 2: Зарегистрировать**
```bash
./scripts/register_appbundle.sh
```

### **Шаг 3: Создать Activity**
```bash
./scripts/register_activity.sh
```

### **Шаг 4: Протестировать**
```bash
./scripts/test_workitem.sh
```

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

