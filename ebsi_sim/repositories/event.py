from ebsi_sim.models import Event
from ebsi_sim.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self):
        super().__init__(Event)