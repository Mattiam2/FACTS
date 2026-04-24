import httpx

from facts_publish.src.repositories.ebsi_base import EBSIClient


class DidrClient(EBSIClient):
    root_path: str

    def __init__(self):
        super().__init__()
        self.root_path = '/did-registry'

    async def get_identifier(self, did: str):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(f"{self.root_path}/identifiers/{did}")
            response.raise_for_status()
            return response.json()

    async def build_create_identifier(self, doc_hash: str):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(f"/track-and-trace/{doc_hash}",
                                         headers={"Content-Type": "application/json"},
                                         json={"jsonrpc": "2.0", "method": "buildDocumentTransaction", "id": 1})
            response.raise_for_status()
            return response.json()