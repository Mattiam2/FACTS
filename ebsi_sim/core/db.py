from contextvars import ContextVar

from sqlmodel import create_engine, Session

from .config import settings

engine = create_engine(settings.db_url, echo=True)

session_ctx = ContextVar("session_ctx", default=None)


class SessionLocal:
    """
    The SessionLocal class provides access to a session instance.

    It is designed to handle session interactions in a thread-safe manner using context-local storage.

    :ivar session: Retrieves or assigns the current session instance.
    :type session: Session | None
    """

    @property
    def session(self) -> Session | None:
        return session_ctx.get()

    @session.setter
    def session(self, value: Session | None):
        session_ctx.set(value)


db = SessionLocal()
