"""
Autodesk APS Client для DWG→DWG обработки с BTE шаблоном
"""

import requests
import time
import logging
from google.cloud import secretmanager

logger = logging.getLogger(__name__)


class APSClient:
    """Клиент для работы с Autodesk APS Design Automation API"""
    
    def __init__(self, project_id="talkhint"):
        self.project_id = project_id
        self.base_url = "https://developer.api.autodesk.com/da/us-east/v3"
        self.client_id = self._get_secret("FORGE_CLIENT_ID")
        self.client_secret = self._get_secret("FORGE_CLIENT_SECRET")
    
    def _get_secret(self, secret_name):
        """Получает секрет из Secret Manager"""
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    
    def get_access_token(self):
        """Получает Access Token от Autodesk"""
        url = "https://developer.api.autodesk.com/authentication/v2/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "code:all data:read data:write"
        }
        
        response = requests.post(url, data=data, timeout=30)
        response.raise_for_status()
        
        return response.json()["access_token"]
    
    def submit_workitem_with_template(self, input_dwg_url, template_url, output_dwg_url, use_bte_activity=False):
        """
        Создает WorkItem для DWG→DWG обработки с BTE шаблоном
        
        Args:
            input_dwg_url: URL входного DWG (публичный или signed)
            template_url: URL BTE шаблона (публичный или signed)
            output_dwg_url: URL для результата (signed PUT)
        
        Returns:
            workitem_id: ID созданного WorkItem
        """
        token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Выбираем Activity в зависимости от параметра
        if use_bte_activity:
            # Кастомная BTE Activity с вставкой шаблона
            # Используем nickname "BotBti" вместо полного Client ID
            activity_id = "BotBti.BTEInsertTemplate+1"
            body = {
                "activityId": activity_id,
                "arguments": {
                    "HostDWG": {
                        "url": input_dwg_url,
                        "verb": "get"
                    },
                    "BteTemplate": {
                        "url": template_url,
                        "verb": "get"
                    },
                    "ResultDWG": {
                        "url": output_dwg_url,
                        "verb": "put"
                    }
                }
            }
            logger.info(f"🎯 Using BTE Activity with template")
        else:
            # Стандартная Activity AutoCAD.PlotToPDF+25_0 (проверено, работает)
            body = {
                "activityId": "AutoCAD.PlotToPDF+25_0",
                "arguments": {
                    "HostDwg": {
                        "url": input_dwg_url
                    },
                    "Result": {
                        "url": output_dwg_url,
                        "verb": "put"
                    }
                }
            }
        
        logger.info(f"📤 Creating WorkItem with activityId: {body['activityId']}")
        logger.info(f"📥 Input DWG: {input_dwg_url[:80]}...")
        if use_bte_activity:
            logger.info(f"📐 Template: {template_url[:80]}...")
        logger.info(f"📤 Output DWG: {output_dwg_url[:80]}...")
        
        response = requests.post(
            f"{self.base_url}/workitems",
            headers=headers,
            json=body,
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            logger.error(f"❌ WorkItem creation failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            response.raise_for_status()
        
        result = response.json()
        workitem_id = result["id"]
        
        logger.info(f"✅ WorkItem created: {workitem_id}")
        return workitem_id
    
    def check_status(self, workitem_id):
        """Проверяет статус WorkItem"""
        token = self.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{self.base_url}/workitems/{workitem_id}",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()
    
    def wait_for_completion(self, workitem_id, timeout_minutes=5):
        """
        Ждет завершения WorkItem
        
        Args:
            workitem_id: ID WorkItem
            timeout_minutes: таймаут в минутах
        
        Returns:
            result: результат обработки
        """
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        last_status = None
        
        logger.info(f"⏳ Waiting for WorkItem {workitem_id}...")
        
        while time.time() - start_time < timeout_seconds:
            result = self.check_status(workitem_id)
            status = result.get("status")
            
            if status != last_status:
                logger.info(f"   Status: {status}")
                last_status = status
            
            if status == "success":
                logger.info(f"🎉 WorkItem completed successfully!")
                stats = result.get("stats", {})
                logger.info(f"   Downloaded: {stats.get('bytesDownloaded', 0)} bytes")
                logger.info(f"   Uploaded: {stats.get('bytesUploaded', 0)} bytes")
                return result
            
            elif status in ["failed", "failedInstructions", "failedDownload", "failedUpload", "cancelled"]:
                logger.error(f"❌ WorkItem failed: {status}")
                if result.get("reportUrl"):
                    logger.error(f"   Report URL: {result.get('reportUrl')}")
                raise Exception(f"WorkItem failed with status: {status}")
            
            time.sleep(5)
        
        raise TimeoutError(f"WorkItem {workitem_id} timed out after {timeout_minutes} minutes")

