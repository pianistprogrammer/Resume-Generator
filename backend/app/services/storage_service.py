"""S3-compatible storage service for file uploads."""

import boto3
from botocore.config import Config
from datetime import datetime
from typing import Optional

from app.config import settings


class StorageService:
    """Service for uploading files to S3-compatible storage (MinIO/S3/R2)."""

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region,
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = settings.s3_bucket_name

    def upload_pdf(self, file_content: bytes, user_id: str, resume_id: str) -> str:
        """
        Upload PDF to S3 and return presigned URL.

        Args:
            file_content: PDF file bytes
            user_id: User ID for organizing files
            resume_id: Resume ID for unique filename

        Returns:
            str: Presigned URL to access the PDF (valid for 7 days)
        """
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"resumes/{user_id}/{resume_id}_{timestamp}.pdf"

        # Upload to S3 (private)
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=filename,
            Body=file_content,
            ContentType='application/pdf'
            # Remove ACL='public-read' to keep it private
        )

        # Generate presigned URL (valid for 7 days)
        presigned_url = self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': filename
            },
            ExpiresIn=604800  # 7 days in seconds
        )

        return presigned_url

    def generate_presigned_url(self, s3_key: str, expires_in: int = 604800) -> str:
        """
        Generate a presigned URL for an existing S3 object.

        Args:
            s3_key: The S3 key (filename) of the object
            expires_in: Expiration time in seconds (default 7 days)

        Returns:
            str: Presigned URL
        """
        presigned_url = self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': s3_key
            },
            ExpiresIn=expires_in
        )
        return presigned_url

    def extract_s3_key_from_url(self, url: str) -> Optional[str]:
        """
        Extract S3 key from a URL or presigned URL.

        Args:
            url: Full URL or presigned URL

        Returns:
            str: S3 key (filename)
        """
        # Handle presigned URLs (contains query parameters)
        if '?' in url:
            url = url.split('?')[0]

        # Extract key from URL
        # Format: https://s3.primeeralabs.com/resumes/resumes/user_id/resume_id.pdf
        parts = url.replace(f"{settings.s3_endpoint_url}/", "").split('/')

        if len(parts) >= 2 and parts[0] == self.bucket_name:
            # Remove bucket name and join the rest
            s3_key = '/'.join(parts[1:])
            return s3_key

        return None

    def delete_pdf(self, pdf_url: str) -> bool:
        """
        Delete PDF from S3.

        Args:
            pdf_url: Full URL to the PDF file

        Returns:
            bool: True if deleted successfully
        """
        try:
            # Extract filename from URL
            filename = pdf_url.replace(f"{settings.s3_public_url}/{self.bucket_name}/", "")

            # Delete from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            return True
        except Exception as e:
            print(f"Error deleting PDF: {e}")
            return False
