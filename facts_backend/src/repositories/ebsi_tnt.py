from facts_backend.src.repositories.ebsi_base import EBSIClient
from facts_backend.src.schemas.document import DocumentPublic


class TntClient(EBSIClient):
    root_path: str

    def __init__(self):
        super().__init__("track-and-trace")

    def get_document(self, doc_hash: str) -> DocumentPublic:
        """
        Retrieve a TNT document based on the provided document hash.

        :param doc_hash: Unique hash string identifying the document.
        :type doc_hash: str
        :return: The TNT document associated with the provided hash.
        :rtype: DocumentPublic
        """
        response = self.get(f"/documents/{doc_hash}")
        document = DocumentPublic.model_validate(response)
        document.hash = doc_hash
        return document

    def get_document_events(self, doc_hash: str):
        """
        Fetches the events associated with a specific TNT document.

        :param doc_hash: A unique string identifier for the document whose events are
            to be retrieved.
        :type doc_hash: str
        :return: The retrieved document events data as a response object.
        :rtype: Any
        """
        response = self.get(f"/documents/{doc_hash}/events")
        return response

    def get_document_accesses(self, doc_hash: str):
        """
        Retrieves accesses information for a specified TNT document.

        :param doc_hash: The unique hash identifier of the document.
        :type doc_hash: str
        :return: The response containing accesses details of the specified document.
        :rtype: Any
        """
        response = self.get(f"/documents/{doc_hash}/accesses")
        return response

    def build_document_transaction(self, access_token: str, from_eth_address: str, transaction_id: int, doc_hash: str, doc_metadata: str, did_ebsi_creator: str):
        """
        Builds and sends a TNT document creation transaction request to the server.

        :param access_token: The access token required for authentication.
        :param from_eth_address: Ethereum address initiating the document transaction.
        :param transaction_id: Unique identifier for the transaction.
        :param doc_hash: Hash of the document to be included in the transaction.
        :param doc_metadata: Metadata describing the document.
        :param did_ebsi_creator: Decentralized Identifier (DID) of the EBSI document creator.
        :return: The server's response to the JSON-RPC request.
        """
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
        """
        Sends a signed transaction to the specified endpoint using the provided access token.

        :param access_token: A string representing the authorization token needed to authenticate
                             the request.
        :param transaction: A dictionary containing the signed transaction details to be sent to
                            the EBSI blockchain.
        :return: The response obtained from the server after the transaction is processed.
        """
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