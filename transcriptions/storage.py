import io
import uuid
import boto3
from django.conf import settings

def put_object_and_presign(data: bytes, content_type: str) -> tuple[str,str]:
    key = f"audio/{uuid.uuid4()}"
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )
    s3.put_object(Bucket=settings.S3_BUCKET, Key=key, Body=io.BytesIO(data), ContentType=content_type)
    presigned = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': settings.S3_BUCKET, 'Key': key},
        ExpiresIn=7*24*3600,
    )
    return key, presigned
