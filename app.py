"""
DWG Processor Core - чистая DWG→DWG обработка через APS
"""

import os
import logging
import uuid
from flask import Flask, request, jsonify
from aps_client import APSClient
from gcs_utils import create_signed_url, create_public_url

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Инициализация APS клиента
aps_client = APSClient()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "dwg-processor-core"})


@app.route('/process-dwg', methods=['POST'])
def process_dwg():
    """
    POST /process-dwg
    
    Request:
    {
        "file_url": "gs://btibot-queue/test_input.dwg",
        "template": "bti_template.dwg"  // опционально
    }
    
    Response:
    {
        "status": "success",
        "workitem_id": "abc123...",
        "output_url": "gs://btibot-processed/result_bti_2025.dwg"
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"status": "error", "message": "No JSON data"}), 400
        
        file_url = data.get("file_url")
        template = data.get("template", "bti_template.dwg")
        
        if not file_url:
            return jsonify({"status": "error", "message": "file_url is required"}), 400
        
        logger.info(f"📥 Processing DWG: {file_url}")
        logger.info(f"📐 Template: {template}")
        
        # Генерируем уникальный ID для задачи
        job_id = str(uuid.uuid4())
        
        # Определяем bucket из file_url
        if file_url.startswith("gs://"):
            bucket_name = file_url.split("/")[2]
        else:
            return jsonify({"status": "error", "message": "Invalid GCS path"}), 400
        
        # Создаем URLs для APS
        # Input DWG (публичный URL, если bucket публичный)
        input_dwg_url = create_public_url(file_url)
        
        # Template URL (публичный из templates/)
        template_path = f"gs://{bucket_name}/templates/{template}"
        template_url = create_public_url(template_path)
        
        # Output DWG (signed PUT URL)
        output_path = f"gs://{bucket_name}/processed/dwg/{job_id}/result.dwg"
        output_dwg_url = create_signed_url(output_path, method="PUT", expiration_hours=1)
        
        logger.info(f"📤 Submitting to APS...")
        
        # Создаем WorkItem в APS
        workitem_id = aps_client.submit_workitem_with_template(
            input_dwg_url=input_dwg_url,
            template_url=template_url,
            output_dwg_url=output_dwg_url
        )
        
        logger.info(f"⏳ Waiting for completion...")
        
        # Ждем завершения
        result = aps_client.wait_for_completion(workitem_id, timeout_minutes=5)
        
        if result.get("status") == "success":
            logger.info(f"✅ Processing complete: {output_path}")
            
            return jsonify({
                "status": "success",
                "workitem_id": workitem_id,
                "output_url": output_path,
                "job_id": job_id,
                "stats": result.get("stats", {})
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"WorkItem failed: {result.get('status')}",
                "workitem_id": workitem_id
            }), 500
    
    except Exception as e:
        logger.exception(f"❌ Error processing DWG: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

