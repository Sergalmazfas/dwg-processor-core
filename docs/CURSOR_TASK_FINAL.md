# 🧭 CURSOR_TASK.md — Автоматическая сборка и регистрация AppBundle

**Дата:** 2025-10-08  
**Цель:** Полная автоматизация AppBundle от компиляции до теста на Autodesk APS  
**Официальная документация:** https://aps.autodesk.com/en/docs/design-automation/v3/

---

## 🎯 Цель задачи

Собрать DLL-плагин `InsertTemplate.dll` с помощью **PowerShell скрипта** (без установленного AutoCAD),  
создать ZIP-архив AppBundle, зарегистрировать его в Autodesk APS,  
создать Activity и выполнить тестовый WorkItem для команды **INSERTBTE**.

**Подтвердить выполнение команды INSERTBTE в отчёте от Autodesk.**

---

## ⚙️ Исходные данные

```
Репозиторий:  https://github.com/Sergalmazfas/dwg-processor-core
Ветка:        feature/create-appbundle
Папка:        bte-appbundle/
Файлы:        ✅ Все созданы и готовы
```

**Структура:**
```
bte-appbundle/
├── build_dll.ps1                 ✅ PowerShell скрипт автосборки
├── InsertTemplate.cs             ✅ C# плагин с командой INSERTBTE
├── PackageContents.xml           ✅ Официальный формат Autodesk
├── package.json                  ✅ Метаданные AppBundle
├── Contents/Windows/             ⏳ (будет создан InsertTemplate.dll)
└── scripts/
    ├── register_appbundle.py     ✅ Регистрация AppBundle
    ├── upload_appbundle.py       ✅ Загрузка ZIP на S3
    ├── register_activity.py      ✅ Создание Activity
    ├── test_workitem.py          ✅ Тест WorkItem
    └── verify_report.sh          ✅ Проверка отчета
```

---

## 🧩 ПОЛНЫЙ ПЛАН ВЫПОЛНЕНИЯ

### **1️⃣ Сборка DLL (PowerShell автоматизация)**

**Официальная документация:** https://help.autodesk.com/view/OARX/2025/ENU/

```powershell
cd bte-appbundle
pwsh build_dll.ps1
```

**Что происходит:**
1. ✅ Скачивает AutoCAD SDK DLLs с GitHub (без установки AutoCAD!)
2. ✅ Компилирует `InsertTemplate.cs` → `Contents/Windows/InsertTemplate.dll`
3. ✅ Создает ZIP архив `InsertTemplateAppBundle.zip`
4. ✅ Готов к регистрации!

**Ожидаемый вывод:**
```
🔧 BTE AppBundle DLL Builder
✅ SDK DLLs downloaded
⚙️ Compiling InsertTemplate.dll...
🎉 DLL compiled successfully! (XX KB)
📦 Creating AppBundle ZIP...
✅ AppBundle ZIP created successfully! (XX KB)
```

**Проверка:**
```bash
ls -lh Contents/Windows/InsertTemplate.dll
ls -lh InsertTemplateAppBundle.zip
```

---

### **2️⃣ Регистрация AppBundle в APS**

**Официальный API:** https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/appbundles-POST/

```bash
cd scripts
python register_appbundle.py
```

**Что происходит:**
1. ✅ Автоматически получает токен из Secret Manager
2. ✅ POST `/appbundles` - создает AppBundle в APS
3. ✅ Получает `uploadParameters` (S3 URL)
4. ✅ Сохраняет `upload_params.json`

**Ожидаемый вывод:**
```
📦 РЕГИСТРАЦИЯ APPBUNDLE В AUTODESK APS
✅ Token получен
   Nickname: BotBti
✅ AppBundle создан!
   ID: BotBti.InsertTemplateAppBundle
   Version: 1
📤 Upload parameters сохранены: upload_params.json
```

---

### **3️⃣ Загрузка ZIP на S3**

```bash
python upload_appbundle.py
```

**Что происходит:**
1. ✅ Читает `upload_params.json`
2. ✅ Загружает `InsertTemplateAppBundle.zip` на S3 сервера Autodesk
3. ✅ AppBundle доступен для Activities

**Ожидаемый вывод:**
```
📤 ЗАГРУЗКА APPBUNDLE НА S3
✅ ZIP файл: ../InsertTemplateAppBundle.zip
✅ Upload params: upload_params.json
📤 Uploading to S3...
✅ AppBundle загружен успешно!
```

---

### **4️⃣ Создание Activity с AppBundle**

**Официальный API:** https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/activities-POST/

```bash
python register_activity.py
```

**Что происходит:**
1. ✅ POST `/activities` - создает Activity
2. ✅ Activity использует `BotBti.InsertTemplateAppBundle+1`
3. ✅ commandLine: `/al $(appbundles[InsertTemplateAppBundle].path)`
4. ✅ settings.script: `INSERTBTE\nQSAVE\nQUIT\n`

**Ожидаемый вывод:**
```
⚙️ СОЗДАНИЕ ACTIVITY С APPBUNDLE
   Nickname: BotBti
✅ Activity создана!
   ID: BotBti.BTEInsertActivity
   Version: 1
   AppBundle: BotBti.InsertTemplateAppBundle+1
   Command: INSERTBTE → QSAVE → QUIT
```

---

### **5️⃣ Тест WorkItem с INSERTBTE**

**Официальный API:** https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/workitems-POST/

```bash
python test_workitem.py
```

**Что происходит:**
1. ✅ POST `/workitems` - создает WorkItem
2. ✅ Activity: `BotBti.BTEInsertActivity+1`
3. ✅ Input: DWG файл из GCS (15 KB)
4. ✅ Output: Signed URL для результата
5. ✅ Polling до завершения (5 минут max)

**Ожидаемый вывод:**
```
🧪 ТЕСТИРОВАНИЕ WORKITEM С INSERTBTE
   Nickname: BotBti
   Input: Plan 2025-10-03... (15 KB)
   Output (signed): ...result_insertbte.dwg
✅ WorkItem создан: 0330e5167bd343f0b939e6fe336e0bfe
   [0s] Status: pending
   [5s] Status: inprogress
   [10s] Status: inprogress
   [15s] Status: success
🎉 WorkItem выполнен УСПЕШНО!
   Downloaded: 15000 bytes
   Uploaded: 16000 bytes
📋 Report URL сохранен: report_url.txt
```

---

### **6️⃣ Проверка отчета**

```bash
bash verify_report.sh
```

**Что происходит:**
1. ✅ Скачивает `report.log` от Autodesk
2. ✅ Проверяет наличие команды `INSERTBTE`
3. ✅ Проверяет загрузку AppBundle
4. ✅ Подтверждает выполнение

**✅ УСПЕШНЫЙ РЕЗУЛЬТАТ:**
```
🔍 ПРОВЕРКА ОТЧЕТА AUTODESK APS
📥 Скачивание отчета от Autodesk...
✅ Отчет скачан: insertbte_report.log (2500 bytes)

🔍 ПРОВЕРКА ВЫПОЛНЕННЫХ КОМАНД
✅ Команда INSERTBTE найдена в отчете!
   Command: INSERTBTE
   🔸 Starting BTE template insertion...
   ✅ BTE template processing complete

✅ Команда QSAVE найдена
✅ Команда QUIT найдена

🔍 ПРОВЕРКА APPBUNDLE
✅ AppBundle загружен на сервере Autodesk!
   Loading AppBundle: InsertTemplateAppBundle
   AppBundle loaded successfully

📊 ИТОГОВАЯ ПРОВЕРКА
🎉 ВСЕ КОМАНДЫ ВЫПОЛНЕНЫ УСПЕШНО!
✅ INSERTBTE - найдено
✅ QSAVE - найдено
✅ QUIT - найдено

🎯 BTE AppBundle работает на серверах Autodesk!
```

---

### **7️⃣ Коммит результатов**

```bash
cd ../..  # Вернуться в корень репозитория
git add bte-appbundle/
git commit -m "✅ AppBundle fully tested on Autodesk APS (INSERTBTE confirmed)"
git push origin feature/create-appbundle
```

---

### **8️⃣ Создание релиза v1.2.0**

```bash
git tag -a v1.2.0 -m "Release v1.2.0: BTE AppBundle integration (INSERTBTE)"
git push origin v1.2.0
```

---

## 📈 Ожидаемый результат

| Этап | Статус | Файл результата |
|------|--------|-----------------|
| DLL сборка | ✅ | `Contents/Windows/InsertTemplate.dll` |
| ZIP архив | ✅ | `InsertTemplateAppBundle.zip` |
| AppBundle зарегистрирован | ✅ | `upload_params.json` |
| ZIP загружен на S3 | ✅ | - |
| Activity создана | ✅ | `activity_info.json` |
| WorkItem выполнен | ✅ | `workitem_id.txt` |
| INSERTBTE в отчёте | ✅ | `insertbte_report.log` |
| Релиз v1.2.0 | 🚀 | Git tag |

---

## 📚 Проверенные официальные источники

✅ **APS Design Automation v3:**  
   https://aps.autodesk.com/en/docs/design-automation/v3/

✅ **AppBundle POST API:**  
   https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/appbundles-POST/

✅ **Activities POST API:**  
   https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/activities-POST/

✅ **WorkItems POST API:**  
   https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/workitems-POST/

✅ **AutoCAD .NET API:**  
   https://help.autodesk.com/view/OARX/2025/ENU/

✅ **Official Postman Walkthrough:**  
   https://github.com/autodesk-platform-services/aps-tutorial-postman/tree/master/DA4ACAD

---

## 🏁 После успешного выполнения

### **Создать Pull Request в main:**
```bash
# На GitHub создать PR:
feature/create-appbundle → main
```

### **Обновить production:**
```bash
git checkout main
git merge feature/create-appbundle
git push origin main
```

### **Deploy на Cloud Run:**
```bash
gcloud run deploy dwg-processor-core \
  --source . \
  --project talkhint \
  --region europe-west1
```

---

## ✅ Критерии успеха

- [x] ✅ PowerShell скрипт создан
- [x] ✅ Все Python скрипты регистрации созданы
- [x] ✅ Bash скрипт проверки создан
- [ ] ⏳ DLL скомпилирован через `build_dll.ps1`
- [ ] ⏳ AppBundle зарегистрирован в APS
- [ ] ⏳ Activity создана с AppBundle
- [ ] ⏳ WorkItem выполнен успешно
- [ ] ⏳ Команда INSERTBTE найдена в отчете
- [ ] ⏳ Релиз v1.2.0 создан

**Готово к выполнению! Запускай сборку! 🚀**

