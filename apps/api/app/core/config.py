from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://japan:japan_local_only@127.0.0.1:5433/japan_travel"
    redis_url: str = "redis://127.0.0.1:6380/0"
    cors_origins: str = "http://localhost:3200"
    environment: str = "local"
    s3_endpoint_url: str = "http://127.0.0.1:9010"
    s3_access_key: str = "japan"
    s3_secret_key: str = "japan_local_only"
    s3_bucket: str = "japan-travel"
    smtp_host: str = "127.0.0.1"
    smtp_port: int = 1026

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
