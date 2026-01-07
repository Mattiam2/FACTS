from ebsi_sim.models import Event
from ebsi_sim.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    """
    Handles the storage and retrieval operations of Event instances.
    """
    def __init__(self):
        super().__init__(Event)