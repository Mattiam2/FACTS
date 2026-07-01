from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FACTS Publish"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "facts"
    DB_PROTOCOL: str = "postgresql"

    AUTH_SECRET_KEY: str = "secret"
    AUTH_TOKEN_EXPIRE_MINUTES: int = 60

    EBSI_URL: str = "http://127.0.0.1:8000"

    TRACKER_PARAMS: list[str] = [
        # Google's Urchin Tracking Module
        "utm_source",
        "utm_medium",
        "utm_term",
        "utm_campaign",
        "utm_content",
        "utm_name",
        "utm_cid",
        "utm_reader",
        "utm_viz_id",
        "utm_pubreferrer",
        "utm_swu",
        # Adobe Omniture SiteCatalyst
        "ICID",
        "icid",
        # Hubspot
        "_hsenc",
        "_hsmi",
        # Marketo
        "mkt_tok",
        # MailChimp
        "mc_cid",
        "mc_eid",
        # comScore Digital Analytix
        "ns_source",
        "ns_mchannel",
        "ns_campaign",
        "ns_linkname",
        "ns_fee",
        # Simple Reach
        "sr_share",
        # Vero
        "vero_conv",
        "vero_id",
        # Non-prefixy and 1-offs
        "fbclid",  # Facebook Click Identifier
        "igshid",  # Instagram Share Identifier
        "srcid",
        "gclid",  # Google Click Identifier
        "ocid",  # Some other Google Click thing
        "ncid",
        "nr_email_referer",
        "ref",  # Generic-ish. Facebook, Product Hunt and others
        "spm",  # Alibaba-family 'super position model' tracker
        "embedded-checkout",
        "__cf_chl_f_tk"
    ]

    PROJECT_ROOT: str = str(Path(__file__).resolve().parent.parent)

    # ES256K
    ISSUER_AUTHENTICATION_PUBLIC_KEY: str = '04364c7a761f55a0dfb9aaa2ed5154c19731615499a41673d36d48c64a91424cf3c82fcf553b8e958a84a823686ef501c7d54897592485af380aff752ab6b0a976'
    ISSUER_AUTHENTICATION_PRIVATE_KEY: str = '85dc97223047209717ecb80290dd1131bd39be142d05707fbf12c045ada6c1d5'
    ISSUER_AUTHENTICATION_VMETHOD_ID: str = 'did:ebsi:zE971oT9esuKdcHspKdfAXg#NigSloq5YZrtXc2A40SO0VkKsEP3Nlqim2V6w4voNKM'
    ISSUER_DID: str = "did:ebsi:zE971oT9esuKdcHspKdfAXg"

    # ES256
    ISSUER_ASSERTION_PUBLIC_KEY: str = b"-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAErgu6fVLzZ8lExaqXcIeZ+YCyL1P2\npFgjV3P4tOi7OeXN2JBwWDzfoYy9gPaQhWf31ZyYJLTBhFV7eHWIKfc3PA==\n-----END PUBLIC KEY-----\n"
    ISSUER_ASSERTION_PRIVATE_KEY: str = b"-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgg1Z50fbmQc4S4YeX\n9es9TX39qsVXz8Ze3frlwTnhwhShRANCAASuC7p9UvNnyUTFqpdwh5n5gLIvU/ak\nWCNXc/i06Ls55c3YkHBYPN+hjL2A9pCFZ/fVnJgktMGEVXt4dYgp9zc8\n-----END PRIVATE KEY-----\n"
    ISSUER_ASSERTION_VMETHOD_ID: str = 'did:ebsi:zE971oT9esuKdcHspKdfAXg#pjyiTxPXALmmH4/ZBxgoUSibpzzKCntMXlzyPGYzupI'

    @property
    def db_url(self):
        return f"{self.DB_PROTOCOL}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"



settings = Settings()
