from facts_backend.src.repositories.ebsi_base import EBSIClient


class DidrClient(EBSIClient):

    def __init__(self):
        super().__init__("did-registry")

    def get_identifier(self, did: str):
        response = self.get(f"/identifiers/{did}")
        return response

    def build_create_identifier(self, doc_hash: str):
        response = self.post(f"/track-and-trace/{doc_hash}",
                             data={"jsonrpc": "2.0", "method": "buildDocumentTransaction", "id": 1})
        return response
