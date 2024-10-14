import tempfile
import io
import sys
import uuid
from boto3 import session
from ....config import config as config_env

STORAGE_ACCESS_KEY_ID = config_env.STORAGE_ACCESS_KEY_ID
STORAGE_SECRET_KEY = config_env.STORAGE_SECRET_KEY
STORAGE_ENDPOINT = config_env.STORAGE_ENDPOINT
STORAGE_BUCKET = config_env.STORAGE_BUCKET

# Initiate session
session = session.Session()
client = session.client('s3',
                        region_name='nyc3',
                        endpoint_url=f'https://{STORAGE_ENDPOINT}',
                        aws_access_key_id=STORAGE_ACCESS_KEY_ID,
                        aws_secret_access_key=STORAGE_SECRET_KEY)


def save_stream_to_tempfile(file_stream: io.BytesIO, filename: str) -> str:
    # Crea un archivo temporal en el sistema
    with tempfile.NamedTemporaryFile(delete=False, suffix=filename, mode='wb') as temp_file:
        # Escribe el contenido del stream en el archivo temporal
        temp_file.write(file_stream.getvalue())
        # Obtén la ruta del archivo temporal
        temp_path = temp_file.name
    return temp_path


def generate_unique_filename(extension: str = '') -> str:
    unique_id = uuid.uuid4().hex
    return f"{unique_id}{extension}"

async def upload_file(file, object_name=None, folder_name=None):

    try:
        if object_name is None:
            object_name = generate_unique_filename(extension='.' + file.filename.split('.')[-1])

        if folder_name is None:
            folder_name = 'new-folder'

        # Upload a file to your Space
        file_stream = io.BytesIO(file.file.read())
        temp_path  = save_stream_to_tempfile(file_stream, object_name)

        #file path, bucket name, object name
        print("file.content_type=====>", file.content_type)
        client.upload_file(temp_path, STORAGE_BUCKET, f'{folder_name}/{object_name}', ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type})
        file_url = f"https://{STORAGE_BUCKET}.{STORAGE_ENDPOINT}/{folder_name}/{object_name}"
        return file_url
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        return None