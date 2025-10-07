"""
GCS Utilities для работы с signed URLs
Создание GET/PUT signed URLs для Autodesk APS
"""

import json
from datetime import timedelta
from google.cloud import storage, secretmanager
from google.oauth2 import service_account


def get_service_account_credentials(project_id="talkhint"):
    """Получает Service Account credentials из Secret Manager"""
    secret_client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/FORGE_SERVICE_KEY/versions/latest"
    secret_response = secret_client.access_secret_version(request={"name": secret_name})
    sa_credentials_json = json.loads(secret_response.payload.data.decode("UTF-8"))
    return service_account.Credentials.from_service_account_info(sa_credentials_json)


def create_signed_url(gcs_path, method="GET", expiration_hours=1):
    """
    Создает signed URL для GCS файла
    
    Args:
        gcs_path: gs://bucket/path/to/file
        method: GET или PUT
        expiration_hours: время жизни URL в часах
    
    Returns:
        signed_url: подписанный URL
    """
    # Парсим GCS path
    if not gcs_path.startswith("gs://"):
        raise ValueError(f"Invalid GCS path: {gcs_path}")
    
    parts = gcs_path.replace("gs://", "").split("/", 1)
    bucket_name = parts[0]
    blob_name = parts[1] if len(parts) > 1 else ""
    
    # Получаем credentials
    sa_credentials = get_service_account_credentials()
    
    # Создаем GCS client с SA credentials
    gcs_client = storage.Client(credentials=sa_credentials)
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # Создаем signed URL
    # ВАЖНО: НЕ указываем content_type для PUT - APS не отправляет этот header!
    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=expiration_hours),
        method=method
    )
    
    return signed_url


def create_public_url(gcs_path):
    """
    Создает публичный URL для GCS файла
    
    Args:
        gcs_path: gs://bucket/path/to/file
    
    Returns:
        public_url: публичный URL
    """
    if not gcs_path.startswith("gs://"):
        raise ValueError(f"Invalid GCS path: {gcs_path}")
    
    # gs://bucket/path -> https://storage.googleapis.com/bucket/path
    return gcs_path.replace("gs://", "https://storage.googleapis.com/")


def upload_to_gcs(local_path, gcs_path):
    """
    Загружает файл в GCS
    
    Args:
        local_path: путь к локальному файлу
        gcs_path: gs://bucket/path/to/file
    """
    # Парсим GCS path
    parts = gcs_path.replace("gs://", "").split("/", 1)
    bucket_name = parts[0]
    blob_name = parts[1]
    
    # Загружаем
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    
    return gcs_path


def download_from_gcs(gcs_path, local_path):
    """
    Скачивает файл из GCS
    
    Args:
        gcs_path: gs://bucket/path/to/file
        local_path: куда сохранить
    """
    # Парсим GCS path
    parts = gcs_path.replace("gs://", "").split("/", 1)
    bucket_name = parts[0]
    blob_name = parts[1]
    
    # Скачиваем
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(local_path)
    
    return local_path

