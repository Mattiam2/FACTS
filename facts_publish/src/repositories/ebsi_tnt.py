from facts_publish.src.repositories.ebsi_base import EBSIClient
from facts_publish.src.schemas.document import DocumentPublic


class TntRepository(EBSIClient):
    root_path: str

    def __init__(self):
        super().__init__("track-and-trace")

    def get_document(self, doc_hash: str) -> DocumentPublic:
        response = self.get(f"/documents/{doc_hash}")
        return DocumentPublic.model_validate(response)

    def get_document_events(self, doc_hash: str):
        response = self.get(f"/documents/{doc_hash}/events")
        return response

    def get_document_accesses(self, doc_hash: str):
        response = self.get(f"/documents/{doc_hash}/accesses")
        return response

    def build_document_transaction(self, doc_hash: str):
        response = self.post(f"/{doc_hash}",
                  data={"jsonrpc": "2.0", "method": "buildDocumentTransaction", "id": 1})
        return response
