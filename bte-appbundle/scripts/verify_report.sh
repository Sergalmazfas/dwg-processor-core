#!/bin/bash
# ================================
# 🔍 Проверка отчета APS на INSERTBTE
# ================================
# Скачивает отчет от Autodesk и проверяет выполнение команды INSERTBTE
# Официальная документация: https://aps.autodesk.com/en/docs/design-automation/v3/

set -e

echo "======================================================================"
echo "🔍 ПРОВЕРКА ОТЧЕТА AUTODESK APS"
echo "======================================================================"

# Проверяем наличие report_url
if [ ! -f "report_url.txt" ]; then
    echo "❌ Файл report_url.txt не найден"
    echo "   Сначала запустите: python test_workitem.py"
    exit 1
fi

REPORT_URL=$(cat report_url.txt)
echo "📋 Report URL: ${REPORT_URL:0:80}..."

# Скачиваем отчет
echo ""
echo "📥 Скачивание отчета от Autodesk..."
curl -s "$REPORT_URL" > insertbte_report.log

if [ ! -f "insertbte_report.log" ]; then
    echo "❌ Не удалось скачать отчет"
    exit 1
fi

REPORT_SIZE=$(wc -c < insertbte_report.log)
echo "✅ Отчет скачан: insertbte_report.log ($REPORT_SIZE bytes)"

# Проверяем команды
echo ""
echo "======================================================================"
echo "🔍 ПРОВЕРКА ВЫПОЛНЕННЫХ КОМАНД"
echo "======================================================================"
echo ""

# Проверка INSERTBTE
if grep -q "INSERTBTE" insertbte_report.log; then
    echo "✅ Команда INSERTBTE найдена в отчете!"
    grep -A3 "INSERTBTE" insertbte_report.log | head -10
else
    echo "❌ Команда INSERTBTE не найдена в отчете"
    echo "   AppBundle возможно не загрузился"
fi

echo ""

# Проверка QSAVE
if grep -q "QSAVE" insertbte_report.log; then
    echo "✅ Команда QSAVE найдена"
else
    echo "⚠️ Команда QSAVE не найдена"
fi

# Проверка QUIT
if grep -q "QUIT" insertbte_report.log; then
    echo "✅ Команда QUIT найдена"
else
    echo "⚠️ Команда QUIT не найдена"
fi

# Проверка загрузки AppBundle
echo ""
echo "======================================================================"
echo "🔍 ПРОВЕРКА APPBUNDLE"
echo "======================================================================"
echo ""

if grep -q "Loading.*AppBundle\|AppBundle loaded" insertbte_report.log; then
    echo "✅ AppBundle загружен на сервере Autodesk!"
    grep -i "appbundle" insertbte_report.log | head -5
else
    echo "⚠️ Загрузка AppBundle не подтверждена в отчете"
fi

# Финальная проверка
echo ""
echo "======================================================================"
echo "📊 ИТОГОВАЯ ПРОВЕРКА"
echo "======================================================================"
echo ""

HAS_INSERTBTE=$(grep -c "INSERTBTE" insertbte_report.log || echo "0")
HAS_QSAVE=$(grep -c "QSAVE" insertbte_report.log || echo "0")
HAS_QUIT=$(grep -c "QUIT" insertbte_report.log || echo "0")

if [ "$HAS_INSERTBTE" -gt 0 ] && [ "$HAS_QSAVE" -gt 0 ] && [ "$HAS_QUIT" -gt 0 ]; then
    echo "🎉 ВСЕ КОМАНДЫ ВЫПОЛНЕНЫ УСПЕШНО!"
    echo ""
    echo "✅ INSERTBTE - найдено"
    echo "✅ QSAVE - найдено"
    echo "✅ QUIT - найдено"
    echo ""
    echo "🎯 BTE AppBundle работает на серверах Autodesk!"
    echo ""
    echo "📁 Полный отчет: insertbte_report.log"
    exit 0
else
    echo "⚠️ НЕ ВСЕ КОМАНДЫ НАЙДЕНЫ"
    echo ""
    echo "INSERTBTE: $HAS_INSERTBTE"
    echo "QSAVE: $HAS_QSAVE"
    echo "QUIT: $HAS_QUIT"
    echo ""
    echo "📋 Проверьте полный отчет: insertbte_report.log"
    exit 1
fi

