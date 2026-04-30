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

    def build_document_transaction(self):
        response = self.post(f"/jsonrpc",
                             data={
                                 "jsonrpc": "2.0",
                                 "method": "createDocument",
                                 "params": [
                                     {
                                         "from": "0xaB6415d6A931A84Dfc02FFD551C4876048c39A92",
                                         "documentHash": "0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67",
                                         "documentMetadata": "0x74657374206d65746164617461",
                                         "didEbsiCreator": "did:ebsi:z95paQoBwGAqnnu4RKTmCtT"
                                     }
                                 ],
                                 "id": 474
                             })
        return response
