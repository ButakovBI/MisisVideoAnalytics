from pydantic import BaseSettings


class Settings(BaseSettings):
    S3_ACCESS_KEY: str
    S3_BUCKET: str
    S3_ENDPOINT: str
    S3_SECRET_KEY: str

    DB_HOST: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_PORT: str = "5432"
    DB_USER: str

    KAFKA_BOOTSTRAP_SERVERS: str

    HEARTBEAT_INTERVAL = 5  # seconds
    RUNNER_ID: str = "runner_1"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
