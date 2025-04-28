import os
import uuid
from django.core.files.storage import Storage
from supabase import create_client, Client
from django.conf import settings
from django.core.files.base import ContentFile
from urllib.parse import urljoin

class SupabaseStorage(Storage):
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL") or getattr(settings, "SUPABASE_URL", None)
        # Use service_role key for server-side operations only
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None)
        self.bucket_name = os.getenv("SUPABASE_BUCKET") or getattr(settings, "SUPABASE_BUCKET", "media")
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and Service Role Key must be set in environment variables or settings.")
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def _save(self, name, content):
        # Upload file content to Supabase storage bucket
        file_content = content.read()
        # Generate unique filename to avoid conflicts
        base, ext = os.path.splitext(name)
        unique_name = f"{base}_{uuid.uuid4().hex}{ext}"
        response = self.client.storage.from_(self.bucket_name).upload(unique_name, file_content)
        # Check for error attribute in response
        if hasattr(response, "error") and response.error is not None:
            raise Exception(f"Failed to upload file to Supabase: {response.error.message}")
        return unique_name

    def _open(self, name, mode='rb'):
        # Download file content from Supabase storage bucket
        response = self.client.storage.from_(self.bucket_name).download(name)
        if hasattr(response, "error") and response.error is not None:
            raise Exception(f"Failed to download file from Supabase: {response.error.message}")
        return ContentFile(response)

    def exists(self, name):
        # Check if file exists in Supabase storage bucket
        response = self.client.storage.from_(self.bucket_name).list(path=name)
        return len(response) > 0

    def url(self, name):
        # Return the public URL of the file
        return urljoin(self.supabase_url, f"/storage/v1/object/public/{self.bucket_name}/{name}")
