import hashlib
import uuid

import rlp
from eth_account._utils.legacy_transactions import Transaction
from fastapi import Depends

from facts_backend.src import utils
from facts_backend.src.core.auth import User
from facts_backend.src.core.exceptions import FACTSError, FACTSDuplicateError, FACTSAuthError, FACTSNotFoundError, \
    FACTSRequestError
from facts_backend.src.repositories.ebsi_tnt import TntClient
from facts_backend.src.repositories.facts import AssessmentRepository
from facts_backend.src.schemas.assessment import AssessmentCreate, AssessmentMetadataPublic
from facts_backend.src.schemas.shared import BuildTransactionResponse, SignedTransactionPayload


class AssessmentServiceError(FACTSError):
    """
    Represents an error specific to Assessment service operations (Status Code: 500).
    """
    pass


class AssessmentServiceDuplicateError(AssessmentServiceError, FACTSDuplicateError):
    """
    Represents an error raised when a duplicate entry is detected (Status Code: 409).
    """
    pass


class AssessmentServiceAuthError(AssessmentServiceError, FACTSAuthError):
    """
    Represents an Assessment service authentication error (Status Code: 401).
    """
    pass


class AssessmentServiceNotFoundError(AssessmentServiceError, FACTSNotFoundError):
    """
    Represents an error raised when a specific resource is not found (Status Code: 404).
    """
    pass


class AssessmentServiceRequestError(AssessmentServiceError, FACTSRequestError):
    """
    Represents an error that occurs during an Assessment service request.
    """
    pass


class AssessmentService:
    tnt_client: TntClient
    assessment_repository: AssessmentRepository

    def __init__(self, tnt_client: TntClient = Depends(), assessment_repository: AssessmentRepository = Depends()):
        self.tnt_client = tnt_client
        self.assessment_repository = assessment_repository

    def get_assessment_document(self, document_hash: str):
        """
        Fetches the assessment from FACTS DB by its hash identifier. If the assessment is not found or is not
        marked as confirmed in the system, an exception is raised. The retrieved assessment is then
        fetched from EBSI TNT API.

        :param document_hash: Unique hash of the assessment document.
        :type document_hash: str
        :return: The assessment document associated with the given hash if it exists
            and is confirmed.
        :rtype: object
        :raises AssessmentServiceNotFoundError: If the assessment document is not
            found or is not confirmed.
        """
        facts_assessment = self.assessment_repository.get(document_hash)
        if not facts_assessment or not facts_assessment.confirmed:
            raise AssessmentServiceNotFoundError(f"Assessment with hash {document_hash} not found")
        return self.tnt_client.get_document(document_hash)

    def get_assessments_list(self, did_creator: str | None = None, article_hash: str | None = None,
                             article_url: str | None = None, offset: int = 0, page_size: int = 100):
        """
        Fetches a list of assessments based on the provided filters and pagination
        parameters.

        :param did_creator: The DID of the creator of the assessment. If None, assessments created by any user are included.
        :param article_hash: The unique hash of the article associated with the
            assessments. If None, assessments for all articles are included.
        :param article_url: The URL of the article associated with the assessments.
            If None, assessments for all article URLs are included.
        :param offset: The starting point for the list of assessments to be returned.
            This parameter is useful for paginated data. Default value is 0.
        :param page_size: The maximum number of assessments to return for each page.
            This parameter is used for pagination. Default value is 100.
        :return: A list of assessments that match the specified parameters.
        :rtype: list
        """
        assessments = self.assessment_repository.list(creator=did_creator, confirmed=True, article_hash=article_hash,
                                                      article_url=article_url, offset=offset, limit=page_size,
                                                      order_by="timestamp")
        return assessments

    def head_assessments_list(self, did_creator: str | None = None, article_hash: str | None = None,
                              article_url: str | None = None):
        """
        Determines whether there are confirmed assessments for a given article or creator.

        :param did_creator: The decentralized identifier (DID) of the creator associated
            with the assessments. If None, this parameter is not included in the query.
        :type did_creator: str | None
        :param article_hash: A hash value representing the article associated with the
            assessments. If None, this parameter is not included in the query.
        :type article_hash: str | None
        :param article_url: The URL of the article associated with the assessments. If None,
            this parameter is not included in the query.
        :type article_url: str | None
        :return: True if there are confirmed assessments meeting the specified criteria;
            False otherwise.
        :rtype: bool
        """
        return self.assessment_repository.count(creator=did_creator, confirmed=True, article_hash=article_hash,
                                                article_url=article_url) > 0

    def get_assessments_evidences(self, document_hash: str):
        """
        Retrieves the evidences associated with a confirmed assessment identified by the given
        document hash.

        :param document_hash: The hash of assessment.
        :type document_hash: str
        :return: The list of evidences associated with the assessment.
        :rtype: list
        :raises AssessmentServiceNotFoundError: If the assessment is not found or has not been
            confirmed.
        """
        assessment = self.assessment_repository.get(document_hash)
        if not assessment or not assessment.confirmed:
            raise AssessmentServiceNotFoundError(f"Assessment with hash {document_hash} not found")
        return assessment.evidences

    def request_create_assessment(self, user: User, payload: AssessmentCreate):
        """
        Creates a new assessment entry in the system and initiates the process for
        building a transaction for the assessment data. This function checks for duplications and normalizes the article's URL

        :param user: The user initiating the request. The user must have valid
            credential attributes like `credential_subject.id`, `verifiable_credential`, and `ebsi_access_token`.
        :type user: User
        :param payload: Contains the assessment creation data, including the assessment's
            information, evidences, and associated Ethereum address.
        :type payload: AssessmentCreate
        :return: A response object containing the created transaction details.
        :rtype: dict
        :raises AssessmentServiceDuplicateError: If an existing assessment  is already confirmed in the system.
        """
        assessment_uuid = uuid.uuid4()
        full_hashable_content = "FACTS_ASSESSMENT:" + str(assessment_uuid)
        document_hash = "0x" + hashlib.sha256(full_hashable_content.encode()).hexdigest()

        normalized_url = utils.normalize_url(payload.assessment_info.article_url)
        article_hash = utils.hash_url(payload.assessment_info.article_url)

        existing_assessment = self.assessment_repository.get(document_hash)
        if existing_assessment and existing_assessment.confirmed:
            raise AssessmentServiceDuplicateError(f"Assessment already exists")
        elif existing_assessment and not existing_assessment.confirmed:
            self.assessment_repository.delete(id=document_hash)

        existing_assessment_article = self.assessment_repository.list(article_hash=article_hash,
                                                                      creator=user.credential_subject.id)
        if existing_assessment_article and existing_assessment_article[0].confirmed:
            raise AssessmentServiceDuplicateError(f"Assessment for article {payload.assessed_article} already exists")
        elif existing_assessment_article and not existing_assessment_article[0].confirmed:
            self.assessment_repository.delete(id=existing_assessment_article[0].hash)

        from_eth_address = payload.from_eth_address
        user_did = user.credential_subject.id
        user_vc = user.verifiable_credential
        ebsi_access_token = user.ebsi_access_token

        assessment_metadata = AssessmentMetadataPublic(version="1.0", assessed_article=payload.assessed_article,
                                                       assessment_info=payload.assessment_info,
                                                       eth_address=from_eth_address, fact_checker_vc=user_vc)
        manipulation_score = assessment_metadata.assessment_info.manipulation_evaluation.score.value if assessment_metadata.assessment_info.manipulation_evaluation else None
        credibility_score = assessment_metadata.assessment_info.credibility_evaluation.score.value if assessment_metadata.assessment_info.credibility_evaluation else None

        build_response = self.build_create_transaction(from_eth_address, user_did, ebsi_access_token, document_hash,
                                                       assessment_metadata)
        transaction: dict = build_response.transaction

        unsigned_transaction_data = bytes.fromhex(transaction['data'].replace("0x", ""))
        data_hash = hashlib.sha256(unsigned_transaction_data).hexdigest()
        self.assessment_repository.create(hash=document_hash, article_hash=article_hash, article_url=normalized_url,
                                          creator=user_did, tx_hash=None, data_hash=data_hash,
                                          eth_address=from_eth_address, manipulation_score=manipulation_score,
                                          credibility_score=credibility_score, confirmed=False)
        for evidence_value in payload.assessment_info.evidences:
            evidence_hash = None
            if evidence_value.startswith("http"):
                evidence_hash = utils.hash_url(evidence_value)
                evidence_value = utils.normalize_url(evidence_value)
            self.assessment_repository.add_evidence(assessment_hash=document_hash, evidence_value=evidence_value,
                                                    evidence_hash=evidence_hash)
        return build_response

    def confirm_create_assessment(self, user: User, document_hash: str, transaction: SignedTransactionPayload):
        """
        Confirms and finalizes the creation of an assessment by validating the provided signed transaction payload
        and user ownership, ensuring the assessment metadata matches the associated transaction data hash,
        and sending the signed transaction to the blockchain.

        :param user: The user attempting to confirm the creation of the assessment. Must match the creator
            of the unconfirmed assessment in the repository.
        :type user: User
        :param document_hash: The unique hash of the unconfirmed assessment to be confirmed.
        :type document_hash: str
        :param transaction: The payload containing the signed transaction intended for confirmation.
        :type transaction: SignedTransactionPayload
        :return: The response from the blockchain containing confirmation details, including the
            transaction hash.
        :rtype: SignedTransactionResponse
        :raises AssessmentServiceNotFoundError: If no unconfirmed assessments exists with the provided hash.
        :raises AssessmentServiceRequestError: If the assessment is already confirmed, the user is not the owner,
            or the transaction data hash does not match the expected hash.
        """
        unconfirmed_assessment = self.assessment_repository.get(document_hash)
        if unconfirmed_assessment is None:
            raise AssessmentServiceNotFoundError(f"Assessment with hash {document_hash} not found")
        if unconfirmed_assessment.confirmed:
            raise AssessmentServiceRequestError("Assessment already confirmed")
        if unconfirmed_assessment.creator != user.credential_subject.id:
            raise AssessmentServiceRequestError("User does not own the unconfirmed assessment")
        signed_transaction_bytes = bytes.fromhex(transaction.signedRawTransaction.replace("0x", ""))
        signed_decoded_transaction: Transaction = rlp.decode(signed_transaction_bytes, Transaction)
        signed_transaction_data = signed_decoded_transaction['data']
        signed_data_hash = hashlib.sha256(signed_transaction_data).hexdigest()
        if unconfirmed_assessment.data_hash != signed_data_hash:
            raise AssessmentServiceRequestError("Transaction data hash does not match the expected hash")
        signed_transaction_response = self.send_signed_transaction(user, transaction)
        if signed_transaction_response.transaction_hash is not None:
            self.assessment_repository.update(id=document_hash, confirmed=True,
                                              tx_hash=signed_transaction_response.transaction_hash)
        return signed_transaction_response

    def build_create_transaction(self, from_eth_address: str, user_did: str, ebsi_access_token: str, document_hash: str,
                                 payload: AssessmentMetadataPublic) -> BuildTransactionResponse:
        """
        Builds a transaction for creating an on-chain record using the specified parameters.

        :param from_eth_address: The Ethereum from address.
        :type from_eth_address: str
        :param user_did: The DID of the user initiating the transaction.
        :type user_did: str
        :param ebsi_access_token: The access token for interacting with the EBSI.
        :type ebsi_access_token: str
        :param document_hash: The hash of the article to be written to the blockchain.
        :type document_hash: str
        :param payload: Metadata describing the assessment, to be included in the transaction payload.
        :type payload: AssessmentMetadataPublic
        :return: A response object containing the details of the constructed
                 transaction.
        :rtype: BuildTransactionResponse
        """
        return utils.build_create_transaction(self.tnt_client, from_eth_address, user_did, ebsi_access_token,
                                              document_hash, payload=payload)

    def send_signed_transaction(self, user: User, transaction: SignedTransactionPayload):
        """
        Sends a signed transaction using the provided user and transaction details.

        :param user: The user initiating the transaction.
        :type user: User
        :param transaction: The signed transaction payload to be sent.
        :type transaction: SignedTransactionPayload
        :return: The result of the transaction processing.
        :rtype: Any
        """
        return utils.send_signed_transaction(self.tnt_client, user, transaction)
