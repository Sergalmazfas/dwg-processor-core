# 📚 Официальные ресурсы Autodesk APS

**Дата:** 2025-10-07  
**Цель:** Ссылки на официальную документацию для каждого этапа

---

## 🔗 Основные ресурсы

### **1. Autodesk Platform Services (APS) - Главная**
```
https://aps.autodesk.com/
```
Официальный сайт с документацией, примерами, SDK

### **2. Design Automation API - Overview**
```
https://aps.autodesk.com/en/docs/design-automation/v3/
```
Общая документация по Design Automation API v3

### **3. Design Automation for AutoCAD - Tutorials**
```
https://aps.autodesk.com/en/docs/design-automation/v3/tutorials/autocad/
```
Пошаговые туториалы для AutoCAD

### **4. Official Postman Collection - DA4ACAD**
```
https://github.com/autodesk-platform-services/aps-tutorial-postman/tree/master/DA4ACAD
```
**ВАЖНО:** Официальная Postman коллекция с walkthrough для AutoCAD

---

## 📦 AppBundle - Официальная документация

### **Создание AppBundle:**
```
https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/appbundles-POST/
```
POST /appbundles - создание AppBundle

### **Загрузка AppBundle:**
```
POST /appbundles возвращает uploadParameters
Нужно использовать multipart/form-data для загрузки ZIP
```

### **Структура AppBundle для AutoCAD:**
```
AppBundle.zip
├── PackageContents.xml    (обязательно)
├── Contents/
│   └── Windows/
│       └── YourPlugin.dll (обязательно)
```

**PackageContents.xml формат:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<ApplicationPackage>
  <Components>
    <RuntimeRequirements OS="Win64" Platform=".NET" />
    <ComponentEntry AppName="PluginName" ModuleName="./Contents/Windows/Plugin.dll" />
  </Components>
</ApplicationPackage>
```

---

## ⚙️ Activity - Официальная документация

### **Создание Activity:**
```
https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/activities-POST/
```
POST /activities - создание Activity

### **Activity с AppBundle:**
```json
{
  "id": "ActivityName",
  "engine": "Autodesk.AutoCAD+25_0",
  "appbundles": ["Owner.AppBundleName+alias"],
  "commandLine": [
    "$(engine.path)\\accoreconsole.exe",
    "/i", "\"$(args[InputDwg].path)\"",
    "/al", "\"$(appbundles[AppBundleName].path)\"",
    "/s", "\"$(settings[script].path)\""
  ]
}
```

---

## 🔄 WorkItem - Официальная документация

### **Создание WorkItem:**
```
https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/workitems-POST/
```
POST /workitems - запуск обработки

### **WorkItem формат:**
```json
{
  "activityId": "Owner.ActivityName+alias",
  "arguments": {
    "InputDwg": {
      "url": "https://...",
      "verb": "get"
    },
    "OutputDwg": {
      "url": "https://...",
      "verb": "put"
    }
  }
}
```

---

## 📖 Примеры кода

### **GitHub репозитории Autodesk:**

**1. aps-tutorial-postman (ВАЖНО!)**
```
https://github.com/autodesk-platform-services/aps-tutorial-postman
└── DA4ACAD/    ← Walkthrough для AutoCAD
```

**2. forge-tutorial-postman (legacy)**
```
https://github.com/Autodesk-Forge/forge-tutorial-postman
```

**3. Design Automation Samples**
```
https://github.com/Autodesk-Forge/design.automation-csharp-template
```

---

## 🔧 .NET Plugin для AutoCAD

### **AutoCAD .NET API:**
```
https://help.autodesk.com/view/OARX/2025/ENU/
```
Официальная документация AutoCAD .NET API

### **Базовый шаблон плагина:**
```csharp
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;

[assembly: CommandClass(typeof(MyPlugin.Commands))]

namespace MyPlugin
{
    public class Commands
    {
        [CommandMethod("MYCOMMAND")]
        public void MyCommand()
        {
            // Your logic here
        }
    }
}
```

### **Необходимые DLL для компиляции:**
```
C:\Program Files\Autodesk\AutoCAD 2025\acdbmgd.dll
C:\Program Files\Autodesk\AutoCAD 2025\acmgd.dll
C:\Program Files\Autodesk\AutoCAD 2025\accoremgd.dll
```

---

## ✅ Checklist использования документации

- [x] ✅ Проверил главную страницу APS
- [x] ✅ Нашел Design Automation API v3 docs
- [x] ✅ Нашел официальный aps-tutorial-postman
- [ ] ⏳ Изучить walkthrough DA4ACAD
- [ ] ⏳ Проверить примеры AppBundle
- [ ] ⏳ Проверить формат PackageContents.xml
- [ ] ⏳ Проверить API reference для /appbundles
- [ ] ⏳ Проверить API reference для /activities

---

## 🎯 Следующие шаги

### **1. Изучить официальный walkthrough:**
```
https://github.com/autodesk-platform-services/aps-tutorial-postman/tree/master/DA4ACAD
```
Там пошаговый процесс:
- Создание AppBundle
- Регистрация в APS
- Создание Activity
- Запуск WorkItem

### **2. Использовать официальные примеры:**
- Смотреть как они структурируют AppBundle
- Копировать формат PackageContents.xml
- Использовать их подход к регистрации

### **3. Следовать официальным API reference:**
- POST /appbundles
- POST /activities  
- POST /workitems
- Проверять формат запросов

**Всегда сверяться с официальной документацией! 📚**

