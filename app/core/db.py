from contextvars import ContextVar
from sqlmodel import create_engine, Session
from .config import settings

engine = create_engine(settings.db_url)

session_ctx = ContextVar("session_ctx", default=None)


class SessionLocal:

    @property
    def session(self) -> Session | None:
        return session_ctx.get()

    @session.setter
    def session(self, value: Session | None):
        session_ctx.set(value)


db = SessionLocal()
