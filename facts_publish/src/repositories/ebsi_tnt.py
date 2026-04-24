import httpx

from facts_publish.src.repositories.ebsi_base import EBSIClient


class TntClient(EBSIClient):
    root_path: str

    def __init__(self):
        super().__init__()
        self.root_path = '/track-and-trace'

    async def get_document(self, doc_hash: str):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(f"{self.root_path}/documents/{doc_hash}")
            response.raise_for_status()
            return response.json()

    async def get_document_events(self, doc_hash: str):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(f"{self.root_path}/documents/{doc_hash}/events")
            response.raise_for_status()
            return response.json()

    async def get_document_accesses(self, doc_hash: str):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(f"{self.root_path}/documents/{doc_hash}/accesses")
            response.raise_for_status()
            return response.json()

    async def build_document_transaction(self, doc_hash: str):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(f"/track-and-trace/{doc_hash}",
                                         headers={"Content-Type": "application/json"},
                                         json={"jsonrpc": "2.0", "method": "buildDocumentTransaction", "id": 1})
            response.raise_for_status()
            return response.json()