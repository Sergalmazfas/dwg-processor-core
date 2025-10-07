#!/usr/bin/env python3
"""
Регистрация AppBundle в Autodesk APS
Официальная документация: https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/appbundles-POST/
"""

import json
import requests
import sys
import os
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
    return response.json()["access_token"], client_id


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
    print("📦 РЕГИСТРАЦИЯ APPBUNDLE В AUTODESK APS")
    print("=" * 70)
    print("\n📚 Официальная документация:")
    print("   https://aps.autodesk.com/en/docs/design-automation/v3/reference/http/appbundles-POST/")
    
    # Проверка ZIP файла
    zip_file = "../InsertTemplateAppBundle.zip"
    if not os.path.exists(zip_file):
        print(f"\n❌ Файл {zip_file} не найден!")
        print("   Сначала создайте ZIP архив:")
        print("   cd .. && zip -r InsertTemplateAppBundle.zip PackageContents.xml Contents package.json")
        return 1
    
    print(f"\n✅ ZIP файл найден: {zip_file}")
    
    # Получаем токен
    print("\n🔸 Получение Access Token...")
    token, client_id = get_access_token()
    print(f"✅ Token получен")
    
    # Получаем nickname
    print("\n🔸 Получение nickname...")
    nickname = get_nickname(token)
    print(f"   Nickname: {nickname}")
    
    # Загружаем package.json
    with open('../package.json', 'r') as f:
        package_data = json.load(f)
    
    # Создаем AppBundle
    print("\n🔸 Создание AppBundle...")
    print(f"   ID: {nickname}.{package_data['id']}")
    
    package_data['id'] = f"{nickname}.{package_data['id']}"
    
    response = requests.post(
        "https://developer.api.autodesk.com/da/us-east/v3/appbundles",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=package_data,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✅ AppBundle создан!")
        print(f"   ID: {result.get('id')}")
        print(f"   Version: {result.get('version')}")
        
        # Сохраняем uploadParameters
        with open('upload_params.json', 'w') as f:
            json.dump(result.get('uploadParameters', {}), f, indent=2)
        
        print(f"\n📤 Upload parameters сохранены: upload_params.json")
        print(f"\n⏭️ Следующий шаг:")
        print(f"   python upload_appbundle.py")
        
        return 0
    elif response.status_code == 409:
        print(f"⚠️ AppBundle уже существует")
        return 0
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(f"   Response: {response.text}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

