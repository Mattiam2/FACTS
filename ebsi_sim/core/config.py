import json

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "EBSI SIMULATOR"
    db_user: str = "postgres"
    db_password: str = "password"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "ebsi"
    db_url: str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    public_key: str = b"-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEb5P/Fz+Agu4M1Ljrxgny12UwJq6T\nLkVLBD7Km5VoD4QXhODiklJFugoTR+HmwwgzkdotRKASS97NTQ3KrrBdTA==\n-----END PUBLIC KEY-----\n"
    private_key: str = b"-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgakYUgjPQkhpF6/pp\nCo+2nd5kwMoYuyb+3J3ZkXqKcxahRANCAARvk/8XP4CC7gzUuOvGCfLXZTAmrpMu\nRUsEPsqblWgPhBeE4OKSUkW6ChNH4ebDCDOR2i1EoBJL3s1NDcqusF1M\n-----END PRIVATE KEY-----\n"

settings = Settings()