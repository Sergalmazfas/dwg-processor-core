# 📚 AppBundle Walkthrough - Официальный подход Autodesk APS

**Источник:** https://github.com/autodesk-platform-services/aps-tutorial-postman/tree/master/DA4ACAD  
**Дата:** 2025-10-07  
**Цель:** Создать AppBundle для вставки BTE шаблона

---

## 🎯 Проблема которую решает AppBundle

### **Текущая ситуация:**
```
❌ Кастомные Activities не работают (Cannot use $LATEST alias)
❌ INSERT команды не выполняются
❌ Стандартная Activity делает только PDF
```

### **Решение через AppBundle:**
```
✅ AppBundle = ZIP с .NET плагином
✅ Плагин выполняет кастомные команды
✅ Activity использует AppBundle
✅ INSERT команда выполняется на серверах Autodesk
```

---

## 📦 Структура AppBundle

### **Что такое AppBundle:**

AppBundle - это ZIP архив с плагином для AutoCAD:

```
InsertTemplateAppBundle.zip
├── PackageContents.xml          # Описание пакета
├── Contents/
│   └── Windows/
│       └── InsertTemplate.dll   # .NET плагин для AutoCAD
└── (необязательно)
    └── bti_template.dwg         # Можно включить шаблон в bundle
```

---

## 🔧 Этапы создания (официальный walkthrough)

### **Этап 1: Создание .NET плагина**

**Файл:** `InsertTemplate.cs`

```csharp
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;

[assembly: CommandClass(typeof(InsertTemplatePlugin.Commands))]

namespace InsertTemplatePlugin
{
    public class Commands
    {
        [CommandMethod("INSERTBTE")]
        public void InsertBTETemplate()
        {
            Document doc = Application.DocumentManager.MdiActiveDocument;
            Database db = doc.Database;
            
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {
                BlockTable bt = tr.GetObject(db.BlockTableId, OpenMode.ForWrite) as BlockTable;
                
                // Вставка блока из шаблона
                using (Database templateDb = new Database(false, true))
                {
                    templateDb.ReadDwgFile("bti_template.dwg", FileOpenMode.OpenForReadAndReadShare, false, "");
                    
                    ObjectIdCollection blockIds = new ObjectIdCollection();
                    BlockTable templateBt = tr.GetObject(templateDb.BlockTableId, OpenMode.ForRead) as BlockTable;
                    
                    foreach (ObjectId btrId in templateBt)
                    {
                        BlockTableRecord btr = tr.GetObject(btrId, OpenMode.ForRead) as BlockTableRecord;
                        if (!btr.IsLayout)
                        {
                            blockIds.Add(btrId);
                        }
                    }
                    
                    IdMapping mapping = new IdMapping();
                    db.WblockCloneObjects(blockIds, bt.Id, mapping, DuplicateRecordCloning.Replace, false);
                }
                
                tr.Commit();
            }
            
            doc.Database.SaveAs("output.dwg", DwgVersion.Current);
        }
    }
}
```

**Компиляция:**
```bash
csc /target:library /reference:"C:\Program Files\Autodesk\AutoCAD 2024\acdbmgd.dll" /reference:"C:\Program Files\Autodesk\AutoCAD 2024\acmgd.dll" InsertTemplate.cs
```

---

### **Этап 2: package.json**

```json
{
  "id": "InsertTemplateAppBundle",
  "engine": "Autodesk.AutoCAD+25_0",
  "description": "Inserts BTE template into DWG"
}
```

---

### **Этап 3: PackageContents.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<ApplicationPackage>
  <Components>
    <RuntimeRequirements OS="Win64" Platform=".NET" SeriesMin="R25.0" SeriesMax="R25.0" />
    <ComponentEntry AppName="InsertTemplate" ModuleName="./Contents/Windows/InsertTemplate.dll" AppDescription="BTE Template Inserter" LoadOnAutoCADStartup="True" />
  </Components>
</ApplicationPackage>
```

---

### **Этап 4: Регистрация AppBundle**

**Шаг 4.1:** Создать AppBundle

```bash
curl -X POST "https://developer.api.autodesk.com/da/us-east/v3/appbundles" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "InsertTemplateAppBundle",
    "engine": "Autodesk.AutoCAD+25_0",
    "description": "Inserts BTE template into DWG"
  }'
```

**Ответ:**
```json
{
  "uploadParameters": {
    "endpointURL": "https://...",
    "formData": {...}
  },
  "id": "BotBti.InsertTemplateAppBundle",
  "version": 1
}
```

**Шаг 4.2:** Загрузить ZIP

```bash
# Создать ZIP
zip -r InsertTemplateAppBundle.zip PackageContents.xml Contents/

# Загрузить на S3 (используя uploadParameters из ответа)
curl -X POST "<endpointURL>" \
  -F key="<formData.key>" \
  -F policy="<formData.policy>" \
  -F content-type="application/octet-stream" \
  -F success_action_status="200" \
  -F success_action_redirect="" \
  -F x-amz-signature="<formData.signature>" \
  -F x-amz-credential="<formData.credential>" \
  -F x-amz-algorithm="<formData.algorithm>" \
  -F x-amz-date="<formData.date>" \
  -F x-amz-server-side-encryption="AES256" \
  -F x-amz-security-token="<formData.token>" \
  -F file=@InsertTemplateAppBundle.zip
```

**Шаг 4.3:** Создать alias

```bash
curl -X POST "https://developer.api.autodesk.com/da/us-east/v3/appbundles/BotBti.InsertTemplateAppBundle/aliases" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id":"prod","version":1}'
```

---

### **Этап 5: Создание Activity с AppBundle**

```bash
curl -X POST "https://developer.api.autodesk.com/da/us-east/v3/activities" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "BTEInsertActivity",
    "engine": "Autodesk.AutoCAD+25_0",
    "appbundles": ["BotBti.InsertTemplateAppBundle+prod"],
    "commandLine": [
      "$(engine.path)\\accoreconsole.exe",
      "/i", "\"$(args[HostDWG].path)\"",
      "/al", "\"$(appbundles[InsertTemplateAppBundle].path)\"",
      "/s", "\"$(settings[script].path)\"",
      "/isolate"
    ],
    "parameters": {
      "HostDWG": {
        "verb": "get",
        "localName": "input.dwg",
        "description": "Input DWG file"
      },
      "ResultDWG": {
        "verb": "put",
        "localName": "output.dwg",
        "description": "Output DWG with BTE template"
      }
    },
    "settings": {
      "script": {
        "value": "INSERTBTE\\nQSAVE\\nQUIT\\n"
      }
    },
    "description": "Inserts BTE template using custom AppBundle"
  }'
```

**После регистрации создать alias:**
```bash
curl -X POST "https://developer.api.autodesk.com/da/us-east/v3/activities/BotBti.BTEInsertActivity/aliases" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"id":"prod","version":1}'
```

---

### **Этап 6: Запуск WorkItem с AppBundle**

```bash
curl -X POST "https://developer.api.autodesk.com/da/us-east/v3/workitems" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "activityId": "BotBti.BTEInsertActivity+prod",
    "arguments": {
      "HostDWG": {
        "url": "https://storage.googleapis.com/btibot-processed/raw/test.dwg",
        "verb": "get"
      },
      "ResultDWG": {
        "url": "<signed_put_url>",
        "verb": "put"
      }
    }
  }'
```

---

## ✅ Ожидаемый результат

### **В отчете должно быть:**

```
[10/07/2025 20:46:32] Loading AppBundle: InsertTemplateAppBundle
[10/07/2025 20:46:32] AppBundle loaded successfully
[10/07/2025 20:46:33] Command: INSERTBTE
[10/07/2025 20:46:33] Inserting BTE template...
[10/07/2025 20:46:33] Template inserted successfully
[10/07/2025 20:46:33] Command: QSAVE
[10/07/2025 20:46:33] Saving document...
[10/07/2025 20:46:33] Command: QUIT
```

### **Размер файла:**
```
Input: 15 KB
Output: > 20 KB (шаблон вставлен!)
```

---

## 📋 Checklist для создания AppBundle

- [ ] Создать .NET плагин (InsertTemplate.cs)
- [ ] Скомпилировать DLL
- [ ] Создать PackageContents.xml
- [ ] Создать package.json
- [ ] Упаковать в ZIP
- [ ] Зарегистрировать AppBundle в APS
- [ ] Загрузить ZIP на S3
- [ ] Создать alias для AppBundle
- [ ] Создать Activity с AppBundle
- [ ] Создать alias для Activity
- [ ] Протестировать WorkItem
- [ ] Проверить отчет (команда INSERTBTE)
- [ ] Проверить размер результата

---

## 🚀 Следующий шаг для Cursor

Создать новую ветку:
```bash
git checkout main
git pull
git checkout -b feature/create-appbundle
```

И начать с создания структуры AppBundle согласно официальному walkthrough.

**Цель:** Получить работающую команду INSERTBTE в отчете от Autodesk! 🎯

