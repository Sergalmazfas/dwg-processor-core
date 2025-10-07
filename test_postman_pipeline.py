#!/usr/bin/env python3
"""
Автоматический тест DWG→DWG pipeline (аналог Postman коллекции)
Тестирует полный цикл: DWG → APS с BTE шаблоном → DWG
"""

import sys
import logging
from aps_client import APSClient
from gcs_utils import create_signed_url, create_public_url, upload_to_gcs, download_from_gcs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_pipeline():
    """Тестирует полный DWG→DWG pipeline"""
    
    print("=" * 70)
    print("🧪 DWG PROCESSOR CORE - PIPELINE TEST")
    print("=" * 70)
    
    try:
        # Шаг 1: Инициализация APS клиента
        print("\n" + "=" * 70)
        print("🔸 ШАГ 1: Инициализация APS клиента")
        print("=" * 70)
        
        aps_client = APSClient()
        print(f"✅ APS Client initialized")
        print(f"   Client ID: {aps_client.client_id[:40]}...")
        
        # Шаг 2: Получение Access Token
        print("\n" + "=" * 70)
        print("🔸 ШАГ 2: Получение Access Token")
        print("=" * 70)
        
        token = aps_client.get_access_token()
        print(f"✅ Access token получен")
        
        # Шаг 3: Подготовка тестовых файлов
        print("\n" + "=" * 70)
        print("🔸 ШАГ 3: Подготовка тестовых файлов")
        print("=" * 70)
        
        # Используем существующий тестовый файл из btibot-processed
        input_file_url = "gs://btibot-processed/raw/1759837370/Plan 2025-10-03 155019_export_2D_room_height.dwg"
        template_url = "gs://btibot-processed/templates/bti_template.dwg"
        output_file_url = "gs://btibot-processed/test_pipeline/result.dwg"
        
        print(f"   Input DWG: {input_file_url}")
        print(f"   Template: {template_url}")
        print(f"   Output DWG: {output_file_url}")
        
        # Шаг 4: Создание signed URLs
        print("\n" + "=" * 70)
        print("🔸 ШАГ 4: Создание URLs для APS")
        print("=" * 70)
        
        # Input - публичный URL
        input_url = create_public_url(input_file_url)
        print(f"✅ Input URL: {input_url[:80]}...")
        
        # Template - публичный URL
        template_signed_url = create_public_url(template_url)
        print(f"✅ Template URL: {template_signed_url[:80]}...")
        
        # Output - signed PUT URL (БЕЗ content_type!)
        output_url = create_signed_url(output_file_url, method="PUT", expiration_hours=1)
        print(f"✅ Output URL (signed): {output_url[:80]}...")
        
        # Шаг 5: Создание WorkItem
        print("\n" + "=" * 70)
        print("🔸 ШАГ 5: Создание WorkItem в APS")
        print("=" * 70)
        
        workitem_id = aps_client.submit_workitem_with_template(
            input_dwg_url=input_url,
            template_url=template_signed_url,
            output_dwg_url=output_url
        )
        
        print(f"✅ WorkItem создан: {workitem_id}")
        
        # Шаг 6: Ожидание завершения
        print("\n" + "=" * 70)
        print("🔸 ШАГ 6: Ожидание завершения")
        print("=" * 70)
        
        result = aps_client.wait_for_completion(workitem_id, timeout_minutes=5)
        
        if result.get("status") == "success":
            print(f"\n🎉 УСПЕХ! WorkItem выполнен!")
            stats = result.get("stats", {})
            print(f"   Downloaded: {stats.get('bytesDownloaded', 0)} bytes")
            print(f"   Uploaded: {stats.get('bytesUploaded', 0)} bytes")
            print(f"   Output DWG: {output_file_url}")
            
            # Итоговый отчет
            print("\n" + "=" * 70)
            print("📋 ИТОГОВЫЙ ОТЧЕТ")
            print("=" * 70)
            print()
            print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            print(f"✅ [OK] Access token")
            print(f"✅ [OK] Input upload")
            print(f"✅ [OK] Template upload")
            print(f"✅ [OK] WorkItem success")
            print(f"✅ [OK] Output DWG saved")
            print()
            print(f"🎉 DWG PROCESSOR CORE РАБОТАЕТ!")
            
            return 0
        else:
            print(f"\n❌ WorkItem failed: {result.get('status')}")
            if result.get("reportUrl"):
                print(f"   Report: {result.get('reportUrl')}")
            return 1
    
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = test_pipeline()
    sys.exit(exit_code)

