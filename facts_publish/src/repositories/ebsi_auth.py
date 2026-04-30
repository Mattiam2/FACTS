import httpx

from facts_publish.src.repositories.ebsi_base import EBSIClient
from facts_publish.src.schemas.auth import EBSITokenPublic


class AuthRepository(EBSIClient):

    def __init__(self):
        super().__init__(root_path="authorisation")

    def get_token(self, data: dict) -> EBSITokenPublic:
        response = self.post("/token", data=data)
        return EBSITokenPublic.model_validate(response)
