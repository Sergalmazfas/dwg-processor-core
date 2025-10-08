#!/usr/bin/env python3
"""
Тестирование WorkItem с INSERTBTE командой
Официальная документация: https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/workitems-POST/
"""

import json
import requests
import time
import sys
import os

# Добавляем путь к gcs_utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from google.cloud import secretmanager
from gcs_utils import create_signed_url, create_public_url


def get_secret(secret_name, project="talkhint"):
    """Получает секрет"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def get_access_token():
    """Получает Access Token"""
    client_id = get_secret("FORGE_CLIENT_ID")
    client_secret = get_secret("FORGE_CLIENT_SECRET")
    
    response = requests.post(
        "https://developer.api.autodesk.com/authentication/v2/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": "code:all"
        },
        timeout=30
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_nickname(token):
    """Получает nickname"""
    response = requests.get(
        "https://developer.api.autodesk.com/da/us-east/v3/forgeapps/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def main():
    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ WORKITEM С INSERTBTE")
    print("=" * 70)
    print("\n📚 Официальная документация:")
    print("   https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/workitems-POST/")
    
    # Получаем токен
    print("\n🔸 Получение Access Token...")
    token = get_access_token()
    print(f"✅ Token получен")
    
    # Получаем nickname
    nickname = get_nickname(token)
    print(f"   Nickname: {nickname}")
    
    # Подготовка файлов
    print("\n🔸 Подготовка файлов...")
    input_url = create_public_url("gs://btibot-processed/raw/1759837370/Plan 2025-10-03 155019_export_2D_room_height.dwg")
    output_url = create_signed_url("gs://btibot-processed/appbundle_test/result_insertbte.dwg", method="PUT")
    
    print(f"   Input: Plan 2025-10-03... (15 KB)")
    print(f"   Output (signed): ...result_insertbte.dwg")
    
    # Создаем WorkItem
    workitem_data = {
        "activityId": f"{nickname}.BTEInsertActivity+1",
        "arguments": {
            "HostDWG": {
                "url": input_url,
                "verb": "get"
            },
            "ResultDWG": {
                "url": output_url,
                "verb": "put"
            }
        }
    }
    
    print(f"\n🔸 Создание WorkItem...")
    print(f"   Activity: {workitem_data['activityId']}")
    
    response = requests.post(
        "https://developer.api.autodesk.com/da/us-east/v3/workitems",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=workitem_data,
        timeout=30
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Ошибка: {response.status_code}")
        print(f"   Response: {response.text}")
        return 1
    
    workitem = response.json()
    workitem_id = workitem["id"]
    
    print(f"✅ WorkItem создан: {workitem_id}")
    
    # Сохраняем для проверки отчета
    with open('workitem_id.txt', 'w') as f:
        f.write(workitem_id)
    
    # Polling
    print(f"\n🔸 Ожидание завершения...")
    
    for i in range(60):  # 5 минут
        time.sleep(5)
        
        status_response = requests.get(
            f"https://developer.api.autodesk.com/da/us-east/v3/workitems/{workitem_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        
        status_data = status_response.json()
        status = status_data.get("status")
        
        print(f"   [{i*5}s] Status: {status}")
        
        if status == "success":
            stats = status_data.get("stats", {})
            report_url = status_data.get("reportUrl")
            
            print(f"\n🎉 WorkItem выполнен УСПЕШНО!")
            print(f"   Downloaded: {stats.get('bytesDownloaded', 0)} bytes")
            print(f"   Uploaded: {stats.get('bytesUploaded', 0)} bytes")
            
            # Сохраняем reportUrl
            if report_url:
                with open('report_url.txt', 'w') as f:
                    f.write(report_url)
                
                print(f"\n📋 Report URL сохранен: report_url.txt")
                print(f"\n⏭️ Следующий шаг:")
                print(f"   bash verify_report.sh")
            
            return 0
        
        elif status in ["failed", "failedInstructions", "failedDownload", "failedUpload"]:
            print(f"\n❌ WorkItem failed: {status}")
            if status_data.get("reportUrl"):
                print(f"   Report: {status_data.get('reportUrl')}")
            return 1
    
    print(f"\n⏱️ Timeout после 5 минут")
    return 1


if __name__ == "__main__":
    sys.exit(main())

