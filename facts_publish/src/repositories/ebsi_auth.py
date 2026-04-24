import httpx

from facts_publish.src.repositories.ebsi_base import EBSIClient


class AuthClient(EBSIClient):
    root_path: str

    def __init__(self):
        super().__init__()
        self.root_path = '/authorisation'

    async def get_token(self, data: dict):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(f"{self.root_path}/token",
                                         headers={"Content-Type": "application/json"},
                                         data=data)
            response.raise_for_status()
            return response.json()
