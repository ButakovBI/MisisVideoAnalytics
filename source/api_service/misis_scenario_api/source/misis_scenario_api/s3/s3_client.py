import aioboto3

from misis_scenario_api.app.config import settings


class S3Client:
    def __init__(self):
        self.session = aioboto3.Session()

    async def upload_video(self, bucket: str,
                           s3_link: str, video_bytes: bytes) -> str:
        async with self.session.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY
        ) as client:
            await client.put_object(
                Bucket=bucket,
                Key=s3_link,
                Body=video_bytes
            )
