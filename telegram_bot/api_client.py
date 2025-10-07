"""
API Client для вызова dwg-processor-core сервиса
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)


class DWGProcessorClient:
    """Клиент для взаимодействия с dwg-processor-core"""
    
    def __init__(self, processor_url=None):
        self.processor_url = processor_url or os.environ.get(
            "DWG_PROCESSOR_URL",
            "https://dwg-processor-core-637190449180.europe-west1.run.app"
        )
    
    def process_dwg(self, file_url, template="bti_template.dwg"):
        """
        Отправляет DWG на обработку в dwg-processor-core
        
        Args:
            file_url: gs://bucket/path/to/file.dwg
            template: название шаблона BTE
        
        Returns:
            result: dict с результатом обработки
        """
        endpoint = f"{self.processor_url}/process-dwg"
        
        payload = {
            "file_url": file_url,
            "template": template
        }
        
        logger.info(f"📤 Sending DWG to processor: {file_url}")
        logger.info(f"🎯 Template: {template}")
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                timeout=600  # 10 минут для долгих обработок
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == "success":
                logger.info(f"✅ Processing complete!")
                logger.info(f"   WorkItem: {result.get('workitem_id')}")
                logger.info(f"   Output: {result.get('output_url')}")
                return result
            else:
                logger.error(f"❌ Processing failed: {result.get('message')}")
                return result
                
        except requests.exceptions.Timeout:
            logger.error("⏱️ Request timeout (10 minutes)")
            return {
                "status": "error",
                "message": "Processing timeout"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def health_check(self):
        """Проверяет доступность dwg-processor-core"""
        try:
            response = requests.get(f"{self.processor_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {"status": "error", "message": str(e)}

