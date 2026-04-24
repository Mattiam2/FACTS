import httpx

from repositories.ebsi_base import EBSIClient


class IssuerClient(EBSIClient):
    root_path: str

    def __init__(self):
        super().__init__()
        self.root_path = '/issuer-mock'

    async def request_vc(self, data: dict):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(f"{self.root_path}/request_vc",
                                         headers={"Content-Type": "application/json"},
                                         json={
                                             "subject_did": data["subject_did"],
                                             "credential_type": data["credential_type"],
                                             "credential_subject": data["credential_subject"]
                                         })
            response.raise_for_status()
            return response.json()
