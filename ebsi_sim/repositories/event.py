from ebsi_sim.models import Event
from ebsi_sim.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    """
    Handles storage and management of Event instances.

    This class is a specialized repository for the Event model. It provides
    mechanisms to interact with the underlying database and perform operations
    related to Event instances. It is built upon the BaseRepository to
    utilize generic repository features tailored for Event objects.
    """
    def __init__(self):
        super().__init__(Event)