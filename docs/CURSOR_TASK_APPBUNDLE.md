# 🧭 CURSOR_TASK.md — Feature: Create AppBundle (.NET InsertTemplate Plugin)

**Ветка:** `feature/create-appbundle`  
**Базовая ветка:** `main`  
**Официальная документация:** https://aps.autodesk.com/en/docs/design-automation/v3/  
**Пример walkthrough:** https://github.com/autodesk-platform-services/aps-tutorial-postman/tree/master/DA4ACAD

---

## 🎯 Цель

Создать, зарегистрировать и протестировать AppBundle для AutoCAD Design Automation (APS).

**Плагин (InsertTemplate.dll) должен:**
1. Выполнять команду `INSERTBTE`
2. Вставлять BTE шаблон в DWG
3. Сохранять результат как DWG
4. Работать на серверах Autodesk

---

## ✅ Текущий прогресс

### **Что создано:**
```
✅ bte-appbundle/
   ✅ InsertTemplate.cs           C# плагин с командой INSERTBTE
   ✅ PackageContents.xml         Официальный формат Autodesk
   ✅ package.json                Метаданные AppBundle
   ✅ README.md                   Документация
   ✅ scripts/
      ✅ register_appbundle.py    Регистрация в APS
```

### **Что требуется:**
```
⏳ Contents/Windows/InsertTemplate.dll    Скомпилированный плагин
⏳ InsertTemplateAppBundle.zip            ZIP архив для загрузки
⏳ Регистрация в APS                      После компиляции DLL
```

---

## ⚙️ Пошаговый план выполнения

### **✅ Шаг 1: Создать ветку** (выполнено)
```bash
git checkout -b feature/create-appbundle
```

### **✅ Шаг 2: Создать структуру** (выполнено)
```
bte-appbundle/
├── Contents/Windows/      ✅
├── PackageContents.xml    ✅
├── package.json           ✅
├── InsertTemplate.cs      ✅
└── scripts/               ✅
```

### **⏳ Шаг 3: Скомпилировать DLL**

**Официальная документация:** https://help.autodesk.com/view/OARX/2025/ENU/

**Требуется:**
- Windows с AutoCAD 2025
- Или Visual Studio с AutoCAD .NET API

**Команда компиляции:**
```bash
csc /target:library /out:Contents/Windows/InsertTemplate.dll InsertTemplate.cs \
    /r:"C:\Program Files\Autodesk\AutoCAD 2025\acdbmgd.dll" \
    /r:"C:\Program Files\Autodesk\AutoCAD 2025\acmgd.dll" \
    /r:"C:\Program Files\Autodesk\AutoCAD 2025\accoremgd.dll"
```

**Альтернатива (для тестирования без DLL):**
Используйте готовый DLL из предыдущих проектов или создайте минимальный DLL.

---

### **⏳ Шаг 4: Создать ZIP архив**

**После компиляции DLL:**
```bash
cd bte-appbundle
zip -r InsertTemplateAppBundle.zip PackageContents.xml Contents package.json
```

**Проверка:**
```bash
unzip -l InsertTemplateAppBundle.zip
# Должно быть:
# - PackageContents.xml
# - Contents/Windows/InsertTemplate.dll
# - package.json
```

---

### **⏳ Шаг 5: Зарегистрировать AppBundle в APS**

**Официальный API:** https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/appbundles-POST/

```bash
cd bte-appbundle/scripts
python register_appbundle.py
```

**Что происходит:**
1. POST /appbundles - создается AppBundle
2. Получаем uploadParameters (S3 URL)
3. Загружаем ZIP на S3
4. Создаем alias "prod"

---

### **⏳ Шаг 6: Создать Activity с AppBundle**

**Официальный API:** https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/activities-POST/

```bash
python register_activity.py
```

**Activity definition:**
```json
{
  "id": "BTEInsertActivity",
  "engine": "Autodesk.AutoCAD+25_0",
  "appbundles": ["BotBti.InsertTemplateAppBundle+prod"],
  "commandLine": [
    "$(engine.path)\\accoreconsole.exe",
    "/i", "\"$(args[HostDWG].path)\"",
    "/al", "\"$(appbundles[InsertTemplateAppBundle].path)\"",
    "/s", "\"$(settings[script].path)\""
  ],
  "parameters": {
    "HostDWG": {"verb": "get"},
    "ResultDWG": {"verb": "put"}
  },
  "settings": {
    "script": {"value": "INSERTBTE\\nQSAVE\\nQUIT\\n"}
  }
}
```

---

### **⏳ Шаг 7: Протестировать WorkItem**

```bash
python test_workitem.py
```

**Проверка:**
1. WorkItem создается
2. Status → success
3. В report.log видна команда `INSERTBTE`
4. Размер output.dwg > 15 KB (шаблон вставлен)

---

### **⏳ Шаг 8: Проверить отчет**

```bash
curl -s "<reportUrl>" | grep -A5 "Command: INSERTBTE"
```

**Ожидается:**
```
Command: INSERTBTE
🔸 Starting BTE template insertion...
🔸 Processing DWG with BTE logic...
✅ BTE template processing complete
✅ File saved as output.dwg
```

---

### **⏳ Шаг 9: Зафиксировать результат**

```bash
git add bte-appbundle/
git commit -m "🧩 Add BTE AppBundle (.NET plugin) and registration scripts"
git push origin feature/create-appbundle
```

---

## ✅ Ожидаемый результат

После выполнения всех шагов:

```
✅ AppBundle InsertTemplateAppBundle зарегистрирован в APS
✅ Activity BotBti.BTEInsertActivity+prod доступна
✅ В отчёте WorkItem появляются команды INSERTBTE, QSAVE, QUIT
✅ DWG на выходе изменён (команда выполнена)
✅ Репозиторий готов к релизу v1.2.0
```

---

## ⚠️ Текущий блокер

**Проблема:** Требуется компиляция DLL

**Решения:**
1. Использовать Windows с AutoCAD для компиляции
2. Использовать готовый DLL из другого проекта
3. Настроить GitHub Actions с Windows runner
4. Пропустить DLL и использовать script-based Activity (ограниченные возможности)

**Рекомендация:** Найти способ получить скомпилированный DLL для продолжения.

---

## 📚 Обязательно проверять документацию

На каждом этапе обращайтесь к:
- ✅ https://aps.autodesk.com/en/docs/design-automation/v3/
- ✅ https://github.com/autodesk-platform-services/aps-tutorial-postman/tree/master/DA4ACAD
- ✅ https://help.autodesk.com/view/OARX/2025/ENU/ (AutoCAD .NET API)

**Готово к продолжению после компиляции DLL! 🚀**

