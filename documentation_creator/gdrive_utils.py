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

def download_document(file_id: str) -> Tuple[Dict, str]:
    gauth = GoogleAuth(settings=gauth_settings)
    gauth.ServiceAuth()
    gdrive_client = GoogleDrive(gauth)
    file = gdrive_client.CreateFile({'id': file_id})
    content = file.GetContentString(mimetype='text/plain')
    full_metadata = file.metadata
    metadata = {
        'title': full_metadata.get('title'),
        'file_type': full_metadata.get('mimeType'),
        'file_link': full_metadata.get('alternateLink'),
        'id': full_metadata.get('id'),
        'owner': full_metadata.get('ownerNames')[0] if full_metadata.get('ownerNames') else None
    }
    return metadata, content

def download_document2(document_id: str) -> Tuple[str, str]:
    service = build('drive', 'v3', credentials=credentials)
    request = service.files().get_media(fileId=document_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    fh.seek(0)
    doc_content = docx2python(fh)
    content = doc_content.text  # extract text from the docx file

    # assuming you want to return the file's metadata as well
    metadata = service.files().get(fileId=document_id).execute()

    return metadata, re.sub(r'(\n)+', '\n', text)

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
        except Exception as e:
            try:
                metadata, content = download_document(file_id)
                documents[file_id] = {
                    'content': content,
                    'metadata': metadata
                }
            except Exception as e:
                print(f"{e}. {file_id}")
    return documents

if __name__=='__main__':
    print(json.dumps(fetch_all_documents('1pvmioD9xQ7vGdSztlvkpmk_R4C2rVSvf'), indent = 2))
