"""Test presigned URL generation."""

from app.services.storage_service import StorageService
from app.config import settings

storage = StorageService()

# Test URL
test_url = "https://s3.primeeralabs.com/resumes/resumes/69a7ef09466d436408171e32/69a824c06d8beab6c021c713_20260304_122536.pdf"

print("Testing presigned URL generation...")
print(f"Original URL: {test_url}")

# Extract S3 key
s3_key = storage.extract_s3_key_from_url(test_url)
print(f"\nExtracted S3 key: {s3_key}")

if s3_key:
    # Generate presigned URL
    presigned_url = storage.generate_presigned_url(s3_key, expires_in=604800)
    print(f"\nPresigned URL (valid for 7 days):")
    print(presigned_url)
    print("\n✅ You can now use this URL to download the PDF")
else:
    print("❌ Failed to extract S3 key from URL")
