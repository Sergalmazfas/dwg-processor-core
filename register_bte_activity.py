#!/usr/bin/env python3
"""
Регистрация BTE Activity в Autodesk APS
"""

import json
import requests
from google.cloud import secretmanager


def get_secret(secret_name, project="talkhint"):
    """Получает секрет из Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def get_access_token(client_id, client_secret):
    """Получает Access Token"""
    url = "https://developer.api.autodesk.com/authentication/v2/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "code:all"
    }
    
    response = requests.post(url, data=data, timeout=30)
    response.raise_for_status()
    return response.json()["access_token"]


def get_nickname(token):
    """Получает nickname приложения"""
    url = "https://developer.api.autodesk.com/da/us-east/v3/forgeapps/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def create_activity(token, nickname, activity_data):
    """Создает Activity в APS"""
    url = "https://developer.api.autodesk.com/da/us-east/v3/activities"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Добавляем префикс nickname к id Activity
    full_id = f"{nickname}.{activity_data['id']}"
    activity_data['id'] = full_id
    
    print(f"📤 Creating Activity: {full_id}")
    print(f"📋 Activity data: {json.dumps(activity_data, indent=2)}")
    
    response = requests.post(url, headers=headers, json=activity_data, timeout=30)
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✅ Activity created successfully!")
        print(f"   ID: {result.get('id')}")
        print(f"   Version: {result.get('version')}")
        return result
    elif response.status_code == 409:
        print(f"⚠️ Activity already exists")
        return {"status": "already_exists"}
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()


def create_activity_alias(token, nickname, activity_name, version, alias="prod"):
    """Создает alias для Activity"""
    url = f"https://developer.api.autodesk.com/da/us-east/v3/activities/{nickname}.{activity_name}/aliases"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    alias_data = {
        "id": alias,
        "version": version
    }
    
    print(f"📌 Creating alias '{alias}' for version {version}")
    
    response = requests.post(url, headers=headers, json=alias_data, timeout=30)
    
    if response.status_code in [200, 201]:
        print(f"✅ Alias created!")
        return response.json()
    elif response.status_code == 409:
        print(f"⚠️ Alias already exists, updating...")
        # Обновляем существующий alias
        patch_url = f"{url}/{alias}"
        response = requests.patch(patch_url, headers=headers, json={"version": version}, timeout=30)
        if response.status_code == 200:
            print(f"✅ Alias updated!")
            return response.json()
    
    print(f"❌ Error: {response.status_code}")
    print(f"Response: {response.text}")
    return None


def main():
    """Основная функция"""
    print("=" * 70)
    print("🔧 BTE ACTIVITY REGISTRATION")
    print("=" * 70)
    
    # Получаем credentials
    print("\n🔑 Getting credentials...")
    client_id = get_secret("FORGE_CLIENT_ID")
    client_secret = get_secret("FORGE_CLIENT_SECRET")
    print(f"   Client ID: {client_id[:40]}...")
    
    # Получаем токен
    print("\n🎫 Getting access token...")
    token = get_access_token(client_id, client_secret)
    print(f"✅ Token obtained")
    
    # Получаем nickname
    print("\n📛 Getting app nickname...")
    nickname = get_nickname(token)
    print(f"   Nickname: {nickname}")
    
    # Загружаем Activity definition
    print("\n📄 Loading Activity definition...")
    with open('aps_activity.json', 'r') as f:
        activity_data = json.load(f)
    
    # Создаем Activity
    print("\n🏗️ Creating Activity...")
    result = create_activity(token, nickname, activity_data)
    
    if result.get("status") != "already_exists":
        version = result.get("version", 1)
        
        # Создаем alias
        print("\n📌 Creating alias...")
        create_activity_alias(token, nickname, "BTEInsertTemplate", version, "prod")
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    print("📋 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 70)
    print()
    print(f"✅ Activity ID: {nickname}.BTEInsertTemplate+prod")
    print(f"✅ Engine: Autodesk.AutoCAD+25_0")
    print(f"✅ Parameters: HostDWG, BteTemplate, ResultDWG")
    print(f"✅ Command: INSERT template → QSAVE → QUIT")
    print()
    print("🎉 BTE Activity готова к использованию!")
    print()
    print("Следующий шаг:")
    print("  python test_bte_activity.py")


if __name__ == "__main__":
    main()

