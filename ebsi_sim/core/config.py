from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "EBSI SIMULATOR"
    db_user: str = "postgres"
    db_password: str = "password"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "ebsi"
    db_url: str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # ES256
    AUTH_PUBLIC_KEY: str = b"-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEb5P/Fz+Agu4M1Ljrxgny12UwJq6T\nLkVLBD7Km5VoD4QXhODiklJFugoTR+HmwwgzkdotRKASS97NTQ3KrrBdTA==\n-----END PUBLIC KEY-----\n"
    AUTH_PRIVATE_KEY: str = b"-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgakYUgjPQkhpF6/pp\nCo+2nd5kwMoYuyb+3J3ZkXqKcxahRANCAARvk/8XP4CC7gzUuOvGCfLXZTAmrpMu\nRUsEPsqblWgPhBeE4OKSUkW6ChNH4ebDCDOR2i1EoBJL3s1NDcqusF1M\n-----END PRIVATE KEY-----\n"

    # ES256K
    ISSUER_AUTHENTICATION_PUBLIC_KEY: str = '04364c7a761f55a0dfb9aaa2ed5154c19731615499a41673d36d48c64a91424cf3c82fcf553b8e958a84a823686ef501c7d54897592485af380aff752ab6b0a976'
    ISSUER_AUTHENTICATION_PRIVATE_KEY: str = '85dc97223047209717ecb80290dd1131bd39be142d05707fbf12c045ada6c1d5'
    ISSUER_AUTHENTICATION_VMETHOD_ID: str = 'did:ebsi:zE971oT9esuKdcHspKdfAXg#NigSloq5YZrtXc2A40SO0VkKsEP3Nlqim2V6w4voNKM'
    ISSUER_DID: str = "did:ebsi:zE971oT9esuKdcHspKdfAXg"

    # ES256
    ISSUER_ASSERTION_PUBLIC_KEY: str = b"-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAErgu6fVLzZ8lExaqXcIeZ+YCyL1P2\npFgjV3P4tOi7OeXN2JBwWDzfoYy9gPaQhWf31ZyYJLTBhFV7eHWIKfc3PA==\n-----END PUBLIC KEY-----\n"
    ISSUER_ASSERTION_PRIVATE_KEY: str = b"-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgg1Z50fbmQc4S4YeX\n9es9TX39qsVXz8Ze3frlwTnhwhShRANCAASuC7p9UvNnyUTFqpdwh5n5gLIvU/ak\nWCNXc/i06Ls55c3YkHBYPN+hjL2A9pCFZ/fVnJgktMGEVXt4dYgp9zc8\n-----END PRIVATE KEY-----\n"
    ISSUER_ASSERTION_VMETHOD_ID: str = 'did:ebsi:zE971oT9esuKdcHspKdfAXg#pjyiTxPXALmmH4/ZBxgoUSibpzzKCntMXlzyPGYzupI'

settings = Settings()
