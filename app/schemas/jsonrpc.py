from enum import Enum

from sqlmodel import SQLModel


class MethodEnum(str, Enum):
    authoriseDid = "authoriseDid"
    createDocument = "createDocument"
    removeDocument = "removeDocument"
    grantAccess = "grantAccess"
    revokeAccess = "revokeAccess"
    writeEvent = "writeEvent"
    sendSignedTransaction = "sendSignedTransaction"


class JsonRpcCreate(SQLModel):
    jsonrpc: str
    id: int
    method: MethodEnum
    params: list[dict]


class JsonRpcPublic(SQLModel):
    jsonrpc: str
    id: int
    result: dict | str