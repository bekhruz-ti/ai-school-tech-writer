from pydrive2.auth import GoogleAuth
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import traceback
from pydrive2.drive import GoogleDrive
from typing import Any, Tuple, Dict
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import re
from docx2python import docx2python
import json
from PyPDF2 import PdfFileReader
from docx import Document
from pydrive2.drive import GoogleDrive

class GoogleDriveSettings(BaseSettings):
    google_project_id: str 
    google_private_key_id: str
    google_private_key: str
    google_client_email: str
    google_client_id: str
    google_auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    google_auth_provider_x509_cert_url: str = "https://www.googleapis.com/oauth2/v1/certs"
    google_token_uri: str = "https://oauth2.googleapis.com/token"
    google_client_x509_cert_url: str

gdrive_settings = GoogleDriveSettings()
private_key_value = gdrive_settings.google_private_key.replace("\\n", "\n")
private_key_with_headers = f'-----BEGIN PRIVATE KEY-----\n{private_key_value}\n-----END PRIVATE KEY-----\n'

gauth_settings = {
    "client_config_backend": "service",
    "service_config": {
        "client_json_dict": {
            "type": "service_account",
            "auth_uri": gdrive_settings.google_auth_uri,
            "token_uri": gdrive_settings.google_token_uri,
            "auth_provider_x509_cert_url": gdrive_settings.google_auth_provider_x509_cert_url,
            "project_id": gdrive_settings.google_project_id,
            "private_key_id": gdrive_settings.google_private_key_id,
            "private_key": private_key_with_headers,
            "client_email": gdrive_settings.google_client_email,
            "client_id": gdrive_settings.google_client_id,
            "client_x509_cert_url": gdrive_settings.google_client_x509_cert_url,
        }
    }
}

credentials = Credentials.from_service_account_info(
    gauth_settings['service_config']['client_json_dict'],
    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
)

class Documents(BaseModel):
    metadata: Dict[str, Any]
    content: str

def download_document(document_id: str) -> Tuple[str, str]:
    service = build('drive', 'v3', credentials=credentials)
    
    # Get the file's metadata
    metadata = service.files().get(fileId=document_id).execute()
    
    # Check if the file is a Google Workspace document
    if 'google-apps' in metadata['mimeType']:
        # Use files.export for Google Workspace documents
        request = service.files().export_media(fileId=document_id, mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    else:
        # Use files.get_media for other file types
        request = service.files().get_media(fileId=document_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    fh.seek(0)
    doc_content = docx2python(fh)

    return metadata, re.sub(r'(\n)+', '\n', doc_content.text)

def download_drive_docs(drive_folder_id: str) -> Dict[str, dict]:
    # Assuming 'credentials' is already defined and authorized
    service = build('drive', 'v3', credentials=credentials)
    
    # List all files in the specified Drive folder
    results = service.files().list(
        q=f"'{drive_folder_id}' in parents",
        fields="nextPageToken, files(id, name, mimeType)").execute()
    
    items = results.get('files', [])
    documents = {}
    
    for item in items:
        file_id = item['id']
        try:
            metadata, content = download_document(file_id)
            documents[file_id] = {
                'content': content,
                'metadata': metadata
            }
            print(f"Downloaded document {file_id}")
        except Exception as e:
            print(f"{e}. {file_id}")
    return documents

if __name__=='__main__':
    result = download_drive_docs('1pvmioD9xQ7vGdSztlvkpmk_R4C2rVSvf')
    print(len(result))
