from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Track 'n' Trace API"
    db_user: str = "postgres"
    db_password: str = "password"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "ebsi"
    db_url: str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


settings = Settings()