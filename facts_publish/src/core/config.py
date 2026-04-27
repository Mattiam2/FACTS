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
    ]

    PROJECT_ROOT: str = str(Path(__file__).resolve().parent.parent)

    @property
    def db_url(self):
        return f"{self.DB_PROTOCOL}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"



settings = Settings()
