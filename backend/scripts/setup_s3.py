"""Script to create S3 bucket for resume storage."""

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.config import settings


def create_bucket():
    """Create S3 bucket if it doesn't exist."""

    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        region_name=settings.s3_region,
        config=Config(signature_version='s3v4')
    )

    bucket_name = settings.s3_bucket_name

    print(f"Checking if bucket '{bucket_name}' exists...")

    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' already exists!")
        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']

        if error_code == '404':
            print(f"Bucket '{bucket_name}' does not exist. Creating...")

            try:
                # Create bucket
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    ACL='public-read'
                )

                print(f"✅ Bucket '{bucket_name}' created successfully!")
                print(f"\nBucket details:")
                print(f"  Name: {bucket_name}")
                print(f"  Endpoint: {settings.s3_endpoint_url}")
                print(f"  Region: {settings.s3_region}")
                print(f"  Public URL: {settings.s3_public_url}/{bucket_name}")

                return True

            except ClientError as create_error:
                print(f"❌ Error creating bucket: {create_error}")
                return False
        else:
            print(f"❌ Error checking bucket: {e}")
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("S3 Bucket Setup")
    print("=" * 60)
    print()

    success = create_bucket()

    if success:
        print("\n✅ Setup complete! You can now generate resumes with PDF downloads.")
    else:
        print("\n❌ Setup failed. Please check your S3 credentials in .env")
        print("\nRequired .env variables:")
        print("  S3_ENDPOINT_URL")
        print("  S3_ACCESS_KEY_ID")
        print("  S3_SECRET_ACCESS_KEY")
        print("  S3_BUCKET_NAME")
        print("  S3_REGION")
        print("  S3_PUBLIC_URL")
