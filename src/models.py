from enum import Enum
from typing import List
from pydantic import BaseModel


class DocumentItem(BaseModel):
    documentId: str
    href: str


class PageLinks(BaseModel):
    first: str
    prev: str
    next: str
    last: str


class DocumentListResponse(BaseModel):
    self: str
    items: List[DocumentItem]
    total: int
    pageSize: int
    links: PageLinks


class Timestamp(BaseModel):
    datetime: str
    source: str
    proof: str

class DocumentResponse(BaseModel):
    metadata: str
    timestamp: Timestamp
    creator: str

class EventItem(BaseModel):
    eventId: str
    href: str

class EventListResponse(BaseModel):
    self: str
    items: List[EventItem]
    total: int
    pageSize: int
    links: PageLinks

class EventResponse(BaseModel):
    metadata: str
    timestamp: Timestamp
    sender: str
    origin: str
    hash: str
    externalHash: str

class VersionEnum(str, Enum):
    latest = "latest"
    deprecated = "deprecated"

class PermissionEnum(str, Enum):
    write = "write"
    delegate = "delegate"
    creator = "creator"

class AccessItem(BaseModel):
    subject: str
    documentId: str
    grantedBy: str
    permission: PermissionEnum

class AccessListResponse(BaseModel):
    self: str
    items: List[AccessItem]
    total: int
    pageSize: int
    links: PageLinks

class MethodEnum(str, Enum):
    authoriseDid = "authoriseDid"
    createDocument = "createDocument"
    removeDocument = "removeDocument"
    grantAccess = "grantAccess"
    revokeAccess = "revokeAccess"
    writeEvent = "writeEvent"
    sendSignedTransaction = "sendSignedTransaction"

class JsonRPCModel(BaseModel):
    jsonrpc: str
    id: int
    method: MethodEnum
    params: list[dict]

class JsonRPCResponse(BaseModel):
    jsonrpc: str
    id: int
    result: dict | str