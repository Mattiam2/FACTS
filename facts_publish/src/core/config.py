from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FACTS Publish"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "facts_indexer"
    DB_PROTOCOL: str = "postgresql"

    EBSI_URL: str = "http://127.0.0.1:8000"

    PROJECT_ROOT: str = str(Path(__file__).resolve().parent.parent)

    @property
    def db_url(self):
        return f"{self.DB_PROTOCOL}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"



settings = Settings()
