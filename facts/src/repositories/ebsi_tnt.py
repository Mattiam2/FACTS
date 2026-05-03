from facts.src.repositories.ebsi_base import EBSIClient
from facts.src.schemas.document import DocumentPublic


class TntRepository(EBSIClient):
    root_path: str

    def __init__(self):
        super().__init__("track-and-trace")

    def get_documents(self) -> list[DocumentPublic]:
        response = self.get(f"/documents")
        docs = []
        for doc in response:
            docs.append(DocumentPublic.model_validate(doc))
        return docs

    def get_document(self, doc_hash: str) -> DocumentPublic:
        response = self.get(f"/documents/{doc_hash}")
        return DocumentPublic.model_validate(response)

    def get_document_events(self, doc_hash: str):
        response = self.get(f"/documents/{doc_hash}/events")
        return response

    def get_document_accesses(self, doc_hash: str):
        response = self.get(f"/documents/{doc_hash}/accesses")
        return response

    def build_document_transaction(self, access_token: str, from_eth_address: str, transaction_id: int, doc_hash: str, doc_metadata: str, did_ebsi_creator: str):
        response = self.post("/jsonrpc",
                             access_token=access_token,
                             data={
                                 "jsonrpc": "2.0",
                                 "method": "createDocument",
                                 "params": [
                                     {
                                         "from": from_eth_address,
                                         "documentHash": doc_hash,
                                         "documentMetadata": doc_metadata,
                                         "didEbsiCreator": did_ebsi_creator
                                     }
                                 ],
                                 "id": transaction_id
                             })
        return response

    def send_signed_transaction(self, access_token: str, transaction: dict):
        response = self.post("/jsonrpc",
                             access_token=access_token,
                             data={
                                 "jsonrpc": "2.0",
                                 "method": "sendSignedTransaction",
                                 "params": [
                                     transaction
                                 ],
                                 "id": 0
                             })
        return response