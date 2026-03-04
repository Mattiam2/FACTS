from ebsi_sim.models.tnt import Access, Document, Event
from ebsi_sim.repositories.base import BaseRepository


class AccessRepository(BaseRepository[Access]):
    """
    Handles the storage and retrieval operations for Access instances.
    """

    def __init__(self):
        super().__init__(Access)


class DocumentRepository(BaseRepository[Document]):
    """
    Handles the storage and retrieval operations for Document instances.
    """

    def __init__(self):
        super().__init__(Document)


class EventRepository(BaseRepository[Event]):
    """
    Handles the storage and retrieval operations of Event instances.
    """
    def __init__(self):
        super().__init__(Event)