import json
from datetime import datetime

from fastapi import Depends
from web3 import Web3
from web3.contract import Contract

from ebsi_sim.core.auth import check_scopes, User
from ebsi_sim.core.config import settings
from ebsi_sim.core.exceptions import AuthError, NotFoundError, RequestError, EBSIError
from ebsi_sim.models.didr import Identifier, VerificationMethod
from ebsi_sim.repositories.didr import IdentifierRepository, IdentifierControllerRepository, \
    VerificationMethodRepository, VerificationRelationshipRepository
from ebsi_sim.schemas import JsonRpcCreate
from ebsi_sim.utils import build_unsigned_transaction, exec_signed_transaction


class DidrServiceError(EBSIError):
    """
    Represents an error specific to DIDR service operations (Status Code: 500).
    """
    pass


class DidrServiceAuthError(DidrServiceError, AuthError):
    """
    Represents an DIDR service authentication error (Status Code: 401).
    """
    pass


class DidrServiceNotFoundError(DidrServiceError, NotFoundError):
    """
    Represents an error raised when a specific resource is not found (Status Code: 404).
    """
    pass


class DidrServiceRequestError(DidrServiceError, RequestError):
    """
    Represents an error that occurs during an DIDR service request.
    """
    pass


class DidrService:
    eth_contract: type[Contract]
    identifier_repository: IdentifierRepository
    identifier_controller_repository: IdentifierControllerRepository
    verification_method_repository: VerificationMethodRepository
    verification_relationship_repository: VerificationRelationshipRepository
    didr_abi: dict

    def __init__(self, identifier_repository: IdentifierRepository = Depends(),
                 identifier_controller_repository: IdentifierControllerRepository = Depends(),
                 verification_method_repository: VerificationMethodRepository = Depends(),
                 verification_relationship_repository: VerificationRelationshipRepository = Depends()):
        self.identifier_repository = identifier_repository
        self.identifier_controller_repository = identifier_controller_repository
        self.verification_method_repository = verification_method_repository
        self.verification_relationship_repository = verification_relationship_repository

        self.didr_abi = json.load(open("ebsi_sim/includes/abi_didr.json", "r"))
        self.eth_contract = Web3().eth.contract(abi=self.didr_abi)

    def get_did_document(self, did: str) -> Identifier | None:
        """
        Retrieves a DID document associated with the provided decentralized identifier
        (DID). If the DID is found in the repository, the corresponding identifier
        object is returned. Otherwise, it returns None.

        :param did: DID of the decentralized identifier to retrieve.
        :type did: str
        :return: An Identifier object associated with the given DID if it exists,
                 otherwise None.
        """
        return self.identifier_repository.get(did)

    def count_did_documents(self, *, controller: str | None = None, **filters):
        """
        Counts the number of DID documents based on the provided filters.

        :param controller: Optional filter specifying the controller of the DID documents.
        :type controller: str | None
        :param filters: Key-value pairs representing filter criteria to apply.
        :type filters: Any
        :return: The count of DID documents matching the provided filters.
        :rtype: int
        """
        return self.identifier_repository.count(controller=controller, **filters)

    def list_did_documents(self, *, offset: int = 0, limit: int = 100, order_by: str | None = None,
                           controller: str | None = None, **filters):
        """
        Retrieves a list of DID documents based on the provided parameters.

        :param offset: The starting position of the records to fetch. Default is 0.
        :type offset: int
        :param limit: The maximum number of records to fetch. Default is 100.
        :type limit: int
        :param order_by: The field by which to order the results. Default is None.
        :type order_by: str | None
        :param controller: Filters the result set by a specific did controller value.
        :type controller: str | None
        :param filters: Key-value pairs representing filter criteria to apply.
        :type filters: Any
        :return: A list of DID documents matching the specified criteria.
        :rtype: list
        """
        return self.identifier_repository.list(offset=offset, limit=limit, order_by=order_by, controller=controller,
                                               **filters)

    def get_verification_method(self, v_method_id: str) -> VerificationMethod | None:
        """
        Retrieve a verification method by its unique identifier.

        :param v_method_id: The unique identifier of a verification method.
        :type v_method_id: str
        :return: The corresponding VerificationMethod object if found, otherwise None.
        """
        return self.verification_method_repository.get(v_method_id)

    def list_verification_methods(self, *, offset: int = 0, limit: int = 100, order_by: str | None = None, **filters) -> \
            list[
                VerificationMethod]:
        """
        Fetch a list of verification methods from the repository filtered by the provided parameters.

        :param offset: The starting position of the records to fetch. Default is 0.
        :type offset: int
        :param limit: The maximum number of records to fetch. Default is 100.
        :type limit: int
        :param order_by: The field by which to order the results. Default is None.
        :type order_by: str | None
        :param filters: Key-value pairs representing filter criteria to apply.
        :type filters: Any
        :return: A list of `VerificationMethod` objects meeting the query criteria.
        """
        return self.verification_method_repository.list(offset=offset, limit=limit, order_by=order_by, **filters)

    def insert_did_document(self, *, did: str, base_document: str, v_method_id: str, public_key: bytes | str,
                            is_secp256k1: bool,
                            not_before: int, not_after: int):
        """
        JSON RPC Method: Inserts a Decentralized Identifier (DID) document along with its associated verification methods and relationships into
        relevant repositories.

        :param did: The DID to be registered.
        :type did: str
        :param base_document: The base context or document structure associated with the DID.
        :type base_document: str
        :param v_method_id: The unique identifier of a verification method.
        :type v_method_id: str
        :param public_key: The public key for the verification method, as bytes or a hexadecimal string.
        :type public_key: bytes | str
        :param is_secp256k1: Bool indicating whether the specified public key uses the Secp256k1 cryptographic curve.
        :type is_secp256k1: bool
        :param not_before: UNIX timestamp indicating the start of the validity period of the verification relationship.
        :type not_before: int
        :param not_after: UNIX timestamp indicating the expiration of the validity period of the verification relationship.
        :type not_after: int
        :return: None
        """
        date_not_before = datetime.fromtimestamp(not_before)
        date_not_after = datetime.fromtimestamp(not_after)

        self.identifier_repository.create(did=did, context=base_document)
        self.identifier_controller_repository.create(identifier_did=did, did_controller=did)

        full_vmethod_id = f"{did}#{v_method_id}"

        if isinstance(public_key, bytes):
            public_key = "0x" + public_key.hex()

        self.verification_method_repository.create(id=full_vmethod_id, did_controller=did,
                                                   type="JsonWebKey2020",
                                                   public_key=public_key, issecp256k1=is_secp256k1,
                                                   notafter=date_not_after)

        self.verification_relationship_repository.create(identifier_did=did, name="capabilityInvocation",
                                                         vmethodid=full_vmethod_id, notbefore=date_not_before,
                                                         notafter=date_not_after)

        self.verification_relationship_repository.create(identifier_did=did, name="authentication",
                                                         vmethodid=full_vmethod_id, notbefore=date_not_before,
                                                         notafter=date_not_after)

    def update_base_document(self, *, did: str, base_document: str):
        """
        JSON RPC Method: Updates the base document for a given identifier.

        :param did: DID to be updated.
        :type did: str
        :param base_document: A string representing the new base document that
            will replace the existing one for the given DID.
        :type base_document: str
        :return: None
        """
        self.identifier_repository.update(id=did, context=base_document)

    def add_controller(self, *, did: str, controller: str):
        """
        JSON RPC Method: Adds a controller to the specified DID.

        :param did: DID to which the controller will be added.
        :type did: str
        :param controller: The DID controller that will be associated with the specified DID.
        :type controller: str
        :return: None
        """
        self.identifier_controller_repository.create(identifier_did=did, did_controller=controller)

    def revoke_controller(self, *, did: str, controller: str):
        """
        JSON RPC Method: Revokes a specific controller for a given DID.

        :param did: DID for which the controller is to be revoked.
        :type did: str
        :param controller: The DID controller to be revoked for the specified DID.
        :type controller: str
        :return: None
        """
        controllers = self.identifier_controller_repository.list(identifier_did=did, did_controller=controller)
        if len(controllers) == 1:
            self.identifier_controller_repository.delete(id=controllers[0].id)

    def add_verification_method(self, *, did: str, v_method_id: str, public_key: bytes | str, is_secp256k1: bool):
        """
        JSON RPC Method: Add a new verification method to an Identifier.

        :param did: DID to associate with the verification method.
        :type did: str
        :param v_method_id: The unique identifier of a verification method.
        :type v_method_id: str
        :param public_key: The public key for the verification method, as bytes or a hexadecimal string.
        :type public_key: bytes | str
        :param is_secp256k1: bool indicating whether the Secp256k1 cryptographic curve is used for the verification method.
        :type is_secp256k1: bool
        :return: None
        """
        full_vmethod_id = f"{did}#{v_method_id}"
        if isinstance(public_key, bytes):
            public_key = "0x" + public_key.hex()
        self.verification_method_repository.create(id=full_vmethod_id, did_controller=did,
                                                   type="JsonWebKey2020",
                                                   public_key=public_key, issecp256k1=is_secp256k1)

    def add_verification_relationship(self, *, did: str, name: str, v_method_id: str, not_before: int, not_after: int):
        """
        JSON RPC Method: Adds a verification relationship to a given DID.

        :param did: DID to which the verification relationship will be associated.
        :type did: str
        :param name: The name of the verification relationship.
        :type name: str
        :param v_method_id: The unique identifier of a verification method.
        :type v_method_id: str
        :param not_before: UNIX timestamp indicating the start of the validity period of the verification relationship.
        :type not_before: int
        :param not_after: UNIX timestamp indicating the expiration of the validity period of the verification relationship.
        :type not_after: int
        :return: None
        """
        not_before_date = datetime.fromtimestamp(not_before)
        not_after_date = datetime.fromtimestamp(not_after)

        full_vmethod_id = f"{did}#{v_method_id}"
        self.verification_relationship_repository.create(identifier_did=did, name=name,
                                                         vmethodid=full_vmethod_id,
                                                         notbefore=not_before_date, notafter=not_after_date)

    def revoke_verification_method(self, *, did: str, v_method_id: str, not_after: int):
        """
        JSON RPC Method: Revokes a specified verification method by marking it as invalid after a given timestamp.

        :param did: DID associated with the verification method.
        :type did: str
        :param v_method_id: The unique identifier of a verification method.
        :type v_method_id: str
        :param not_after: UNIX timestamp indicating the expiration of the validity period of the verification method.
        :type not_after: int
        :return: None.
        :raises DidrServiceRequestError: If the `not_after` timestamp is in the future.
        :raises DidrServiceNotFoundError: If the specified verification method does not exist in the
            database.
        """
        not_after_date = datetime.fromtimestamp(not_after)
        if not_after_date >= datetime.now():
            raise DidrServiceRequestError("Cannot revoke a method with date in the future")

        full_vmethod_id = f"{did}#{v_method_id}"
        vmethod = self.verification_method_repository.get(id=full_vmethod_id)
        if not vmethod:
            raise DidrServiceNotFoundError("Verification method not found")
        self.verification_method_repository.update(id=vmethod.id, notafter=not_after_date)

    def expire_verification_method(self, *, did: str, v_method_id: str, not_after: int):
        """
        JSON RPC Method: Sets the expiration date of a verification method identified by its ID.

        :param did: DID of the entity associated with the verification method.
        :type did: str
        :param v_method_id: The unique identifier of a verification method.
        :type v_method_id: str
        :param not_after: UNIX timestamp indicating the expiration of the validity period of the verification method.
        :type not_after: int
        :return: None
        :raises DidrServiceRequestError: If the provided expiration timestamp is in the past.
        :raises DidrServiceNotFoundError: If the specified verification method does not exist in the repository.
        """
        not_after_date = datetime.fromtimestamp(not_after)
        if not_after_date < datetime.now():
            raise DidrServiceRequestError("Cannot set expiration of a method with date in the past")

        full_vmethod_id = f"{did}#{v_method_id}"
        vmethod = self.verification_method_repository.get(id=full_vmethod_id)
        if not vmethod:
            raise DidrServiceNotFoundError("Verification method not found")
        self.verification_method_repository.update(id=vmethod.id, notafter=not_after_date)

    def _check_scope(self, current_user: User, method: str) -> None:
        """
        Checks if the current user has the necessary authorization to perform the
        specified method.

        :param current_user: The user making the request.
        :type current_user: User
        :param method: The name of the method for which the scope check is performed.
        :type method: str
        :return: None
        :raises DidrServiceAuthError: If the user lacks authorization for the
            specified method.
        """
        is_authorized = check_scopes(current_user, method, {
            "insertDidDocument": ["didr_invite", "didr_write"],
            "updateBaseDocument": ["didr_write"],
            "addService": ["didr_write"],
            "revokeService": ["didr_write"],
            "addController": ["didr_write"],
            "revokeController": ["didr_write"],
            "addVerificationMethod": ["didr_write"],
            "addVerificationRelationship": ["didr_write"],
            "revokeVerificationMethod": ["didr_write"],
            "expireVerificationMethod": ["didr_write"],
            "rollVerificationMethod": ["didr_write"],
            "sendSignedTransaction": ["didr_invite", "didr_write"]
        })
        if not is_authorized:
            raise DidrServiceAuthError("Forbidden method")

    def _check_did_access(self, current_user: User, payload: JsonRpcCreate) -> None:
        """
        Validates whether the given user has the appropriate access rights to perform operations
        on the DID document specified in the payload. The method checks the requested action
        against a predefined set of allowed methods. It also ensures that the provided DID matches
        the user's identifier or confirms the user's control rights over the specified DID.

        :param current_user: The user making the request.
        :type current_user: User
        :param payload: The payload of the JSON-RPC request containing method and parameters.
        :type payload: JsonRpcCreate
        :raises DidrServiceRequestError: If the method in the payload is not allowed, or if the
            specified subject DID does not exist in the DID register.
        :raises DidrServiceAuthError: If the user does not have sufficient permissions to
            operate on the specified subject DID.
        :return: None
        """
        method = payload.method
        subject_did: str | None = payload.params[0].get("did", None) if len(payload.params) > 0 else None
        if method not in ("insertDidDocument", "updateBaseDocument", "addService", "revokeService", "addController",
                          "revokeController", "addVerificationMethod", "addVerificationRelationship",
                          "revokeVerificationMethod", "expireVerificationMethod", "rollVerificationMethod"):
            raise DidrServiceRequestError("Method not allowed")

        if subject_did is not None and subject_did != current_user.sub:
            subject_did: str
            if method == "insertDidDocument":
                raise DidrServiceAuthError("Forbidden DID")
            sub_identifier = self.get_did_document(subject_did)
            if not sub_identifier:
                raise DidrServiceRequestError("Subject identifier not found in DID Register")
            controllers = sub_identifier.controllers
            if current_user.sub not in [c.did for c in controllers]:
                raise DidrServiceAuthError("Forbidden DID")

    def get_abi(self) -> dict:
        """
        Retrieves the ABI (Application Binary Interface).

        The method fetches and returns the DID registry's ABI.

        :return: The ABI associated with the DID registry.
        :rtype: dict
        """
        return self.didr_abi

    def handle_rpc(self, current_user: User, payload: JsonRpcCreate) -> dict | str:
        """
        Handles the RPC request by processing the method specified in the payload and taking appropriate actions.
        Supports creating or executing transactions based on the payload details.

        :param current_user: The user making the request.
        :type current_user: User
        :param payload: The payload of the JSON-RPC request containing method and parameters.
        :type payload: JsonRpcCreate
        :return: The result of executing the JSON-RPC call, either an unsigned or a signed transaction.
        :rtype: dict
        :raises DidrServiceError: If there is an internal error during processing.
        :raises EBSIError: Forwards any application-specific exceptions raised by the underlying methods.
        """
        try:
            params = payload.params[0] if len(payload.params) > 0 else {}
            self._check_scope(current_user, payload.method)
            if payload.method != "sendSignedTransaction":
                self._check_did_access(current_user, payload)
                json_rpc_result = build_unsigned_transaction(self.eth_contract, settings.ETH_ADDRESS, payload.method,
                                                             params)
            else:
                json_rpc_result = exec_signed_transaction(current_user, self.eth_contract, settings.ETH_ADDRESS, self,
                                                          params['unsignedTransaction'],
                                                          params['signedRawTransaction'])
        except EBSIError:
            raise
        except Exception:
            raise DidrServiceError("Internal error")
        else:
            return json_rpc_result
