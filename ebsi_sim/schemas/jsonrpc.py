from enum import Enum

from sqlmodel import SQLModel


class MethodEnum(str, Enum):
    """
    Enumeration of various method types for defining specific actions.

    This class provides an enumeration of method names that represent
    different categorized operations such as authorizing actions, managing
    documents, granting/revoking access, handling events, and performing
    transactions. Each enumeration value is a string representing the method
    type.
    """

    authoriseDid = "authoriseDid"
    createDocument = "createDocument"
    removeDocument = "removeDocument"
    grantAccess = "grantAccess"
    revokeAccess = "revokeAccess"
    writeEvent = "writeEvent"
    sendSignedTransaction = "sendSignedTransaction"


class JsonRpcCreate(SQLModel):
    """
    Represents a JSON-RPC request message for creating resources.

    This class is used to define the structure of a JSON-RPC request object
    to be utilized for creating resources.

    :ivar jsonrpc: The JSON-RPC protocol version used in the request.
    :type jsonrpc: str
    :ivar id: Unique identifier of the JSON-RPC request.
    :type id: int
    :ivar method: The name of the method to invoke for this request.
    :type method: MethodEnum
    :ivar params: Parameters to be passed to the invoked method,
        represented as a list of dictionaries.
    :type params: list[dict]
    """

    jsonrpc: str
    id: int
    method: MethodEnum
    params: list[dict]


class JsonRpcPublic(SQLModel):
    """
    Represents a JSON-RPC response model.

    This class is intended to define the structure of a JSON-RPC response,
    which includes the protocol version, an identification field, and the
    response result.

    :ivar jsonrpc: The JSON-RPC protocol version.
    :type jsonrpc: str
    :ivar id: The identifier for the JSON-RPC request.
    :type id: int
    :ivar result: The result of the JSON-RPC request. Can be a dictionary
        or a string, depending on the nature of the request.
    :type result: dict | str
    """

    jsonrpc: str
    id: int
    result: dict | str