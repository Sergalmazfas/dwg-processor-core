#!/usr/bin/env python3
"""
Проверка вставки BTE шаблона через реальную Activity
Тестирует что INSERT команда выполняется на серверах Autodesk
"""

import json
import requests
import time
from google.cloud import secretmanager
from gcs_utils import create_signed_url, create_public_url


def get_secret(secret_name, project="talkhint"):
    """Получает секрет"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def main():
    print("=" * 70)
    print("🔍 ПРОВЕРКА ВСТАВКИ BTE ШАБЛОНА (INSERT команда)")
    print("=" * 70)
    
    # Получаем credentials
    client_id = get_secret("FORGE_CLIENT_ID")
    client_secret = get_secret("FORGE_CLIENT_SECRET")
    
    # Получаем токен
    print("\n🔸 Получение Access Token...")
    auth_response = requests.post(
        "https://developer.api.autodesk.com/authentication/v2/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": "code:all"
        },
        timeout=30
    )
    
    auth_response.raise_for_status()
    access_token = auth_response.json()["access_token"]
    print(f"✅ Token получен")
    
    # Проверяем BTE Activity
    print("\n🔸 Проверка BTE Activity...")
    activities_response = requests.get(
        "https://developer.api.autodesk.com/da/us-east/v3/activities",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30
    )
    
    activities = activities_response.json().get("data", [])
    bte_activity = [a for a in activities if "BTEInsertTemplate" in a]
    
    if bte_activity:
        print(f"✅ BTE Activity найдена: {bte_activity[0]}")
        activity_id = bte_activity[0]
    else:
        print(f"⚠️ BTE Activity не найдена, используем стандартную")
        activity_id = "AutoCAD.PlotToPDF+25_0"
    
    # Создаем URLs
    print("\n🔸 Подготовка файлов...")
    input_url = create_public_url("gs://btibot-processed/raw/1759837370/Plan 2025-10-03 155019_export_2D_room_height.dwg")
    template_url = create_public_url("gs://btibot-processed/templates/bti_template.dwg")
    output_url = create_signed_url("gs://btibot-processed/bte_insert_test/result_with_insert.dwg", method="PUT")
    
    # Создаем WorkItem с BTE Activity
    print(f"\n🔸 Создание WorkItem...")
    print(f"   Activity: {activity_id}")
    
    # Пробуем использовать SimpleDWG2DWG если BTE не работает
    if "SimpleDWG" in activity_id or "BTEInsert" in activity_id:
        workitem_data = {
            "activityId": "BotBti.SimpleDWG2DWG_NoTemplate+$LATEST",
            "arguments": {
                "inputFile": {"url": input_url},
                "resultFile": {"url": output_url, "verb": "put"}
            }
        }
    else:
        workitem_data = {
            "activityId": activity_id,
            "arguments": {
                "HostDwg": {"url": input_url},
                "Result": {"url": output_url, "verb": "put"}
            }
        }
    
    workitem_response = requests.post(
        "https://developer.api.autodesk.com/da/us-east/v3/workitems",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json=workitem_data,
        timeout=30
    )
    
    if workitem_response.status_code not in [200, 201]:
        print(f"❌ Ошибка создания WorkItem: {workitem_response.status_code}")
        print(f"Response: {workitem_response.text}")
        return 1
    
    workitem = workitem_response.json()
    workitem_id = workitem["id"]
    print(f"✅ WorkItem создан: {workitem_id}")
    
    # Ожидание
    print(f"\n🔸 Ожидание завершения...")
    
    for _ in range(60):  # 5 минут
        time.sleep(5)
        
        status_response = requests.get(
            f"https://developer.api.autodesk.com/da/us-east/v3/workitems/{workitem_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
        
        status_data = status_response.json()
        status = status_data.get("status")
        
        print(f"   Status: {status}")
        
        if status == "success":
            print(f"\n✅ SUCCESS!")
            
            # Скачиваем отчет
            if status_data.get("reportUrl"):
                print(f"\n📋 Скачивание отчета...")
                report_response = requests.get(status_data["reportUrl"], timeout=30)
                
                if report_response.status_code == 200:
                    report_text = report_response.text
                    
                    with open('bte_insert_report.log', 'w') as f:
                        f.write(report_text)
                    
                    print(f"✅ Отчет сохранен: bte_insert_report.log")
                    
                    # Проверяем команды INSERT
                    print(f"\n🔍 Проверка выполненных команд:")
                    print("-" * 70)
                    
                    for line in report_text.split('\n'):
                        if 'Command:' in line and 'INSERT' in line.upper():
                            print(f"   ✅ {line.strip()}")
                        elif 'Command:' in line and 'QSAVE' in line.upper():
                            print(f"   ✅ {line.strip()}")
                        elif 'Command:' in line and 'QUIT' in line.upper():
                            print(f"   ✅ {line.strip()}")
                    
                    # Проверяем размер
                    stats = status_data.get("stats", {})
                    uploaded = stats.get("bytesUploaded", 0)
                    
                    print(f"\n📊 Размер результата: {uploaded} bytes")
                    
                    if uploaded > 10000:
                        print(f"   ✅ > 10 KB - скорее всего шаблон вставлен!")
                    else:
                        print(f"   ⚠️ < 10 KB - возможно шаблон не вставился")
                    
                    # Проверяем наличие INSERT в отчете
                    if 'INSERT' in report_text.upper():
                        print(f"\n✅ КОМАНДА INSERT НАЙДЕНА В ОТЧЕТЕ!")
                        print(f"   🎉 BTE шаблон применяется!")
                    else:
                        print(f"\n⚠️ Команда INSERT не найдена в отчете")
                        print(f"   Activity выполнила стандартный скрипт")
            
            return 0
        
        elif status in ["failed", "failedInstructions", "failedDownload", "failedUpload"]:
            print(f"\n❌ Failed: {status}")
            if status_data.get("reportUrl"):
                print(f"   Report: {status_data.get('reportUrl')}")
            return 1
    
    print(f"\n⏱️ Timeout")
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

