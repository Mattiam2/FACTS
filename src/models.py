from typing import List, Annotated

from fastapi import Query
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

class AccessItem(BaseModel):
    subject: str
    documentId: str
    grantedBy: str
    permission: Annotated[str, Query(regex="(^write$)|(^delegate$)|(^creator$)")]

class AccessListResponse(BaseModel):
    self: str
    items: List[AccessItem]
    total: int
    pageSize: int
    links: PageLinks