import hashlib
import json
import random
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

import rlp
import uuid
from eth_account._utils.legacy_transactions import Transaction
from fastapi import Depends

from facts.src import utils
from facts.src.core.auth import User
from facts.src.core.exceptions import FACTSError, FACTSDuplicateError, FACTSAuthError, FACTSNotFoundError, \
    FACTSRequestError
from facts.src.repositories.ebsi_tnt import TntClient
from facts.src.repositories.facts import AssessmentRepository
from facts.src.schemas.assessment import AssessmentPayload, AssessmentMetadata
from facts.src.schemas.shared import BuildTransactionResponse, SignedTransactionPayload, \
    SignedTransactionResponse


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

    def get_assessment_by_hash(self, document_hash: str):
        facts_assessment = self.assessment_repository.get(document_hash)
        if not facts_assessment or not facts_assessment.confirmed:
            raise AssessmentServiceNotFoundError(f"Assessment with hash {document_hash} not found")
        return self.tnt_client.get_document(document_hash)

    # def get_assessments_by_url(self, url: str):
    #     """
    #     Retrieves an article based on its url.
    #     """
    #     document_hash = self.hash_url(url)
    #     document_element = self.get_article_by_hash(document_hash)
    #     return document_element.metadata_json if document_element.metadata_json else None

    def get_assessments_list(self, did_creator: str | None = None, article_hash: str | None = None, article_url: str | None = None, offset: int = 0, page_size: int = 100):
        assessments = self.assessment_repository.list(creator=did_creator, confirmed=True, article_hash=article_hash, article_url=article_url, offset=offset, limit=page_size, order_by="timestamp")
        return assessments

    def get_assessments_evidences(self, document_hash: str):
        assessment = self.assessment_repository.get(document_hash)
        if not assessment or not assessment.confirmed:
            raise AssessmentServiceNotFoundError(f"Assessment with hash {document_hash} not found")
        return assessment.evidences

    def request_create_assessment(self, user: User, payload: AssessmentPayload):

        assessment_uuid = uuid.uuid4()
        full_hashable_content = "FACTS_ASSESSMENT:" + str(assessment_uuid)
        document_hash = "0x" + hashlib.sha256(full_hashable_content.encode()).hexdigest()

        existing_assessment = self.assessment_repository.get(document_hash)
        if existing_assessment and existing_assessment.confirmed:
            raise AssessmentServiceDuplicateError(f"Assessment already exists")
        elif existing_assessment and not existing_assessment.confirmed:
            self.assessment_repository.delete(id=document_hash)

        from_eth_address = payload.from_eth_address
        user_did = user.credential_subject.id
        user_vc = user.verifiable_credential
        ebsi_access_token = user.ebsi_access_token

        assessment_metadata = AssessmentMetadata(version="1.0", assessed_article=payload.assessed_article, assessment_info=payload.assessment_info, eth_address=from_eth_address, fact_checker_vc=user_vc)
        authenticity_score = assessment_metadata.assessment_info.authenticity_evaluation.score.value if assessment_metadata.assessment_info.authenticity_evaluation else None
        credibility_score = assessment_metadata.assessment_info.credibility_evaluation.score.value if assessment_metadata.assessment_info.credibility_evaluation else None

        build_response = self.build_create_transaction(from_eth_address, user_did, ebsi_access_token, document_hash, assessment_metadata)
        transaction: dict = build_response.transaction

        normalized_url = utils.normalize_url(payload.assessment_info.article_url)
        article_hash = utils.hash_url(payload.assessment_info.article_url)

        unsigned_transaction_data = bytes.fromhex(transaction['data'].replace("0x", ""))
        data_hash = hashlib.sha256(unsigned_transaction_data).hexdigest()
        self.assessment_repository.create(hash=document_hash, article_hash=article_hash, article_url=normalized_url, creator=user_did, tx_hash=None, data_hash=data_hash, eth_address=from_eth_address, authenticity_score=authenticity_score, credibility_score=credibility_score, confirmed=False)
        for evidence_value in payload.assessment_info.evidences:
            evidence_hash = None
            if evidence_value.startswith("http"):
                evidence_hash = utils.hash_url(evidence_value)
                evidence_value = utils.normalize_url(evidence_value)
            self.assessment_repository.add_evidence(assessment_hash=document_hash, evidence_value=evidence_value, evidence_hash=evidence_hash)
        return build_response

    def confirm_create_assessment(self, user: User, document_hash: str, transaction: SignedTransactionPayload):
        unconfirmed_assessment = self.assessment_repository.get(document_hash)
        if unconfirmed_assessment is None:
            raise AssessmentServiceNotFoundError(f"Assessment with hash {document_hash} not found")
        if unconfirmed_assessment.confirmed:
            raise AssessmentServiceRequestError("Assessment already confirmed")
        if unconfirmed_assessment.creator != user.credential_subject.id:
            raise AssessmentServiceRequestError("User does not own the unconfirmed assessment")
        signed_transaction_bytes = bytes.fromhex(transaction.signedRawTransaction)
        signed_decoded_transaction: Transaction = rlp.decode(signed_transaction_bytes, Transaction)
        signed_transaction_data = signed_decoded_transaction['data']
        signed_data_hash = hashlib.sha256(signed_transaction_data).hexdigest()
        if unconfirmed_assessment.data_hash != signed_data_hash:
            raise AssessmentServiceRequestError("Transaction data hash does not match the expected hash")
        signed_transaction_response = self.send_signed_transaction(user, transaction)
        if signed_transaction_response.transaction_hash is not None:
            self.assessment_repository.update(id=document_hash, confirmed=True, tx_hash=signed_transaction_response.transaction_hash)
        return signed_transaction_response

    def build_create_transaction(self, from_eth_address: str, user_did: str, ebsi_access_token: str, document_hash: str, payload: AssessmentMetadata) -> BuildTransactionResponse:
        transaction_id = random.randint(1, 999)
        document_metadata_json = payload.model_dump_json()
        document_metadata_hex = "0x" + document_metadata_json.encode().hex()
        json_rpc_response = self.tnt_client.build_document_transaction(access_token=ebsi_access_token,
                                                                       from_eth_address=from_eth_address,
                                                                       transaction_id=transaction_id,
                                                                       doc_hash=document_hash,
                                                                       doc_metadata=document_metadata_hex,
                                                                       did_ebsi_creator=user_did)
        return BuildTransactionResponse(document_hash=document_hash, transaction=json_rpc_response[
            "result"] if "result" in json_rpc_response else None)

    def send_signed_transaction(self, user: User, transaction: SignedTransactionPayload):
        transaction_dict = transaction.model_dump(mode="json")
        json_rpc_response = self.tnt_client.send_signed_transaction(access_token=user.ebsi_access_token,
                                                                    transaction=transaction_dict)
        return SignedTransactionResponse(
            transaction_hash=json_rpc_response["result"] if "result" in json_rpc_response else None)
