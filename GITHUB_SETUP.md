# 📦 Инструкция по загрузке на GitHub

## Шаг 1: Создать репозиторий на GitHub

1. Откройте https://github.com/new
2. **Repository name:** `dwg-processor-core`
3. **Description:** `Clean DWG→DWG processor via Autodesk APS with BTE template integration`
4. **Visibility:** Public
5. **НЕ добавляйте:** README, .gitignore, license (у нас уже есть)
6. Нажмите **"Create repository"**

---

## Шаг 2: Push кода на GitHub

После создания репозитория выполните:

```bash
cd /Users/seregaboss/dwg-processor-core

# Добавить remote
git remote add origin https://github.com/talkhint/dwg-processor-core.git

# Push код
git push -u origin main
```

---

## Шаг 3: Создать release tag

```bash
# Создать тег v1.0.0
git tag -a v1.0.0 -m "🚀 Release v1.0.0: Clean DWG Processor Core

- DWG→DWG processing via Autodesk APS
- BTE template integration  
- Production-ready with CI/CD
- Auto-testing before deploy"

# Push тег
git push origin v1.0.0
```

---

## Шаг 4: Настроить Cloud Build trigger (опционально)

1. Откройте https://console.cloud.google.com/cloud-build/triggers?project=talkhint
2. **Create Trigger**
3. Настройки:
   - **Name:** `dwg-processor-core-deploy`
   - **Event:** Push to a branch
   - **Source:** talkhint/dwg-processor-core
   - **Branch:** `^main$`
   - **Configuration:** Cloud Build configuration file (yaml or json)
   - **Location:** `cloudbuild.yaml`
4. **Create**

---

## ✅ Проверка

После push проверьте:

1. **Репозиторий:** https://github.com/talkhint/dwg-processor-core
2. **Releases:** https://github.com/talkhint/dwg-processor-core/releases
3. **Cloud Build:** https://console.cloud.google.com/cloud-build/builds?project=talkhint

---

## 📋 Альтернатива: GitHub CLI

Если хотите через CLI:

```bash
# Авторизация
gh auth login

# Создание репозитория и push
gh repo create talkhint/dwg-processor-core \
  --public \
  --source=. \
  --remote=origin \
  --push \
  --description="Clean DWG→DWG processor via Autodesk APS"
```

**Выберите удобный способ! 🚀**

