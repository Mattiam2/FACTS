from core.config import settings


class EBSIClient:
    def __init__(self):
        self.base_url = settings.EBSI_URL