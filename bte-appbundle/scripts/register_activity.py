#!/usr/bin/env python3
"""
Создание Activity с AppBundle в Autodesk APS
Официальная документация: https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/activities-POST/
"""

import json
import requests
import sys
from google.cloud import secretmanager


def get_secret(secret_name, project="talkhint"):
    """Получает секрет из Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def get_access_token():
    """Получает Access Token от Autodesk"""
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
    """Получает nickname приложения"""
    response = requests.get(
        "https://developer.api.autodesk.com/da/us-east/v3/forgeapps/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def main():
    print("=" * 70)
    print("⚙️ СОЗДАНИЕ ACTIVITY С APPBUNDLE")
    print("=" * 70)
    print("\n📚 Официальная документация:")
    print("   https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/activities-POST/")
    
    # Получаем токен
    print("\n🔸 Получение Access Token...")
    token = get_access_token()
    print(f"✅ Token получен")
    
    # Получаем nickname
    print("\n🔸 Получение nickname...")
    nickname = get_nickname(token)
    print(f"   Nickname: {nickname}")
    
    # Создаем Activity
    activity_data = {
        "id": f"{nickname}.BTEInsertActivity",
        "engine": "Autodesk.AutoCAD+25_0",
        "appbundles": [f"{nickname}.InsertTemplateAppBundle+1"],
        "commandLine": [
            "$(engine.path)\\\\accoreconsole.exe",
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
    }
    
    print("\n🔸 Создание Activity...")
    print(f"   ID: {activity_data['id']}")
    print(f"   AppBundle: {activity_data['appbundles'][0]}")
    print(f"   Command: INSERTBTE → QSAVE → QUIT")
    
    response = requests.post(
        "https://developer.api.autodesk.com/da/us-east/v3/activities",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=activity_data,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"\n✅ Activity создана!")
        print(f"   ID: {result.get('id')}")
        print(f"   Version: {result.get('version')}")
        
        # Сохраняем для теста
        with open('activity_info.json', 'w') as f:
            json.dump({
                "id": result.get('id'),
                "version": result.get('version')
            }, f, indent=2)
        
        print(f"\n⏭️ Следующий шаг:")
        print(f"   python test_workitem.py")
        
        return 0
    elif response.status_code == 409:
        print(f"⚠️ Activity уже существует")
        print(f"   ID: {nickname}.BTEInsertActivity")
        return 0
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(f"   Response: {response.text}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

