from facts_backend.src.repositories.ebsi_base import EBSIClient
from facts_backend.src.schemas.auth import EBSITokenPublic


class AuthClient(EBSIClient):

    def __init__(self):
        super().__init__(root_path="authorisation")

    def get_token(self, data: dict) -> EBSITokenPublic:
        response = self.post("/token", data=data)
        return EBSITokenPublic.model_validate(response)
