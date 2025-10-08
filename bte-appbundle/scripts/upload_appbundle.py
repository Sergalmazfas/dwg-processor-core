#!/usr/bin/env python3
"""
Загрузка AppBundle ZIP на S3 (uploadParameters от APS)
Официальная документация: https://aps.autodesk.com/en/docs/design-automation/v3/
"""

import json
import requests
import os


def main():
    print("=" * 70)
    print("📤 ЗАГРУЗКА APPBUNDLE НА S3")
    print("=" * 70)
    
    # Проверяем файлы
    zip_file = "../InsertTemplateAppBundle.zip"
    params_file = "upload_params.json"
    
    if not os.path.exists(zip_file):
        print(f"\n❌ ZIP файл не найден: {zip_file}")
        print("   Сначала запустите: pwsh ../build_dll.ps1")
        return 1
    
    if not os.path.exists(params_file):
        print(f"\n❌ Upload parameters не найдены: {params_file}")
        print("   Сначала запустите: python register_appbundle.py")
        return 1
    
    print(f"✅ ZIP файл: {zip_file}")
    print(f"✅ Upload params: {params_file}")
    
    # Загружаем uploadParameters
    with open(params_file, 'r') as f:
        upload_params = json.load(f)
    
    endpoint_url = upload_params.get("endpointURL")
    form_data = upload_params.get("formData", {})
    
    if not endpoint_url:
        print(f"\n❌ endpointURL не найден в {params_file}")
        return 1
    
    print(f"\n📤 Uploading to S3...")
    print(f"   Endpoint: {endpoint_url[:60]}...")
    
    # Подготавливаем multipart/form-data
    files_data = {}
    for key, value in form_data.items():
        files_data[key] = (None, value)
    
    # Добавляем файл
    with open(zip_file, 'rb') as f:
        files_data['file'] = (os.path.basename(zip_file), f, 'application/octet-stream')
        
        response = requests.post(
            endpoint_url,
            files=files_data,
            timeout=60
        )
    
    if response.status_code in [200, 201, 204]:
        print(f"✅ AppBundle загружен успешно!")
        print(f"\n⏭️ Следующий шаг:")
        print(f"   python register_activity.py")
        return 0
    else:
        print(f"❌ Ошибка загрузки: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

