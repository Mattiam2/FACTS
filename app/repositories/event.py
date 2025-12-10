from app.models import Event
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self):
        super().__init__(Event)