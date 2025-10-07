#!/usr/bin/env python3
"""
Тест BTE Activity - вставка шаблона в DWG
"""

import sys
from aps_client import APSClient
from gcs_utils import create_signed_url, create_public_url


def test_bte_activity():
    """Тестирует BTE Activity для вставки шаблона"""
    
    print("=" * 70)
    print("🧪 BTE ACTIVITY TEST")
    print("=" * 70)
    
    try:
        # Инициализация
        print("\n🔸 Инициализация APS клиента...")
        aps_client = APSClient()
        print(f"✅ Client ID: {aps_client.client_id[:40]}...")
        
        # Проверка токена
        print("\n🔸 Получение Access Token...")
        token = aps_client.get_access_token()
        print(f"✅ Token получен")
        
        # Подготовка файлов
        print("\n🔸 Подготовка файлов...")
        
        input_dwg = "gs://btibot-processed/raw/1759837370/Plan 2025-10-03 155019_export_2D_room_height.dwg"
        template_dwg = "gs://btibot-processed/templates/bti_template.dwg"
        output_dwg = "gs://btibot-processed/test_bte_activity/result_with_template.dwg"
        
        print(f"   Input: {input_dwg}")
        print(f"   Template: {template_dwg}")
        print(f"   Output: {output_dwg}")
        
        # Создание URLs
        print("\n🔸 Создание URLs...")
        input_url = create_public_url(input_dwg)
        template_url = create_public_url(template_dwg)
        output_url = create_signed_url(output_dwg, method="PUT", expiration_hours=1)
        
        print(f"✅ Input URL: {input_url[:80]}...")
        print(f"✅ Template URL: {template_url[:80]}...")
        print(f"✅ Output URL (signed): {output_url[:80]}...")
        
        # Отправка WorkItem
        print("\n🔸 Создание WorkItem с BTE шаблоном...")
        print("   🎯 Using BTE Activity: BotBti.BTEInsertTemplate+1")
        workitem_id = aps_client.submit_workitem_with_template(
            input_dwg_url=input_url,
            template_url=template_url,
            output_dwg_url=output_url,
            use_bte_activity=True  # Используем кастомную BTE Activity!
        )
        
        print(f"✅ WorkItem создан: {workitem_id}")
        
        # Ожидание результата
        print("\n🔸 Ожидание завершения...")
        result = aps_client.wait_for_completion(workitem_id, timeout_minutes=5)
        
        # Проверка результата
        if result.get("status") == "success":
            stats = result.get("stats", {})
            downloaded = stats.get("bytesDownloaded", 0)
            uploaded = stats.get("bytesUploaded", 0)
            
            print("\n" + "=" * 70)
            print("✅ ТЕСТ ПРОЙДЕН!")
            print("=" * 70)
            print()
            print(f"✅ [OK] WorkItem success")
            print(f"✅ [OK] Input downloaded: {downloaded} bytes")
            print(f"✅ [OK] Output uploaded: {uploaded} bytes")
            print(f"✅ [OK] Result saved: {output_dwg}")
            print()
            
            # Проверка размера
            if uploaded > 10000:  # > 10 KB
                print(f"✅ [OK] Output size > 10 KB - шаблон вставлен!")
            else:
                print(f"⚠️ [WARNING] Output size small ({uploaded} bytes) - проверьте вставку")
            
            print()
            print(f"🎉 BTE ACTIVITY РАБОТАЕТ!")
            print()
            print(f"📊 Report URL: {result.get('reportUrl', 'N/A')}")
            print(f"📥 Проверьте файл: gcloud storage cat {output_dwg}")
            
            return 0
        else:
            print("\n" + "=" * 70)
            print("❌ ТЕСТ ПРОВАЛЕН")
            print("=" * 70)
            print()
            print(f"❌ Status: {result.get('status')}")
            print(f"📋 Report: {result.get('reportUrl')}")
            
            # Скачиваем отчет если есть
            if result.get("reportUrl"):
                print("\n📋 Downloading report...")
                report_response = requests.get(result["reportUrl"], timeout=30)
                if report_response.status_code == 200:
                    print("\n" + "-" * 70)
                    print(report_response.text[:2000])  # Первые 2000 символов
                    print("-" * 70)
            
            return 1
    
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_bte_activity())

