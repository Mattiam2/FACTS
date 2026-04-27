import httpx

from facts_publish.src.core.config import settings


class EBSIClient:
    client: httpx.Client

    def __init__(self, root_path: str):
        base_url = f"{settings.EBSI_URL}/{root_path}"
        self.client = httpx.Client(base_url=base_url)

    def get(self, path: str, params: dict = None):
        with self.client as client:
            response = client.get(path, params=params)
            response.raise_for_status()
            return response.json()

    def post(self, path: str, data: dict = None):
        with self.client as client:
            try:
                response = client.post(path, json=data, headers={"Content-Type": "application/json"})
                response.raise_for_status()
            except httpx.HTTPError:
                if response:
                    print(response.json())
                raise
            return response.json()
