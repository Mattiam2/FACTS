from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "EBSI SIMULATOR"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "ebsi"
    DB_PROTOCOL: str = "postgresql"

    JWT_VERIFY_EXP: bool = True

    @property
    def db_url(self):
        return f"{self.DB_PROTOCOL}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # ES256
    AUTH_PUBLIC_KEY: str = b"-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEb5P/Fz+Agu4M1Ljrxgny12UwJq6T\nLkVLBD7Km5VoD4QXhODiklJFugoTR+HmwwgzkdotRKASS97NTQ3KrrBdTA==\n-----END PUBLIC KEY-----\n"
    AUTH_PRIVATE_KEY: str = b"-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgakYUgjPQkhpF6/pp\nCo+2nd5kwMoYuyb+3J3ZkXqKcxahRANCAARvk/8XP4CC7gzUuOvGCfLXZTAmrpMu\nRUsEPsqblWgPhBeE4OKSUkW6ChNH4ebDCDOR2i1EoBJL3s1NDcqusF1M\n-----END PRIVATE KEY-----\n"

    ETH_ADDRESS: str = "0x823BBc0ceE3dE3B61AcfA0CEedb951AB9a013F05"
    ISSUER_DID: str = "did:ebsi:zE971oT9esuKdcHspKdfAXg"

    PROJECT_ROOT: str = str(Path(__file__).resolve().parent.parent)


settings = Settings()
