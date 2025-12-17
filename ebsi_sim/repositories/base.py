from typing import Any, Generic, Iterable, Type, TypeVar
from abc import ABC, abstractmethod
from sqlmodel import SQLModel, select, func

from ebsi_sim.core.db import db

T = TypeVar("T", bound=SQLModel)

class Repository(ABC, Generic[T]):
    @abstractmethod
    def get(self, id: Any) -> T | None: ...
    @abstractmethod
    def list(self, *, offset=0, limit=100,
             order_by: str | None = None, **filters: Any) -> list[T]: ...
    @abstractmethod
    def create(self, **data: Any) -> T: ...
    @abstractmethod
    def update(self, id: Any, **data: Any) -> T: ...
    @abstractmethod
    def delete(self, id: Any) -> None: ...


class BaseRepository(Repository[T]):

    def __init__(self, model: Type[T]):
        self.model = model

    def get(self, id: Any) -> T | None:
        return db.session.get(self.model, id)

    def list(self, *, offset=0, limit=100, order_by=None, **filters: Any) -> list[T]:
        stmt = select(self.model)
        for field, value in filters.items():
            stmt = stmt.where(getattr(self.model, field) == value)
        if order_by:
            stmt = stmt.order_by(getattr(self.model, order_by))
        stmt = stmt.offset(offset).limit(limit)
        return list(db.session.scalars(stmt))

    def create(self, *, commit=True, **data: Any) -> T:
        obj = self.model(**data)  # type: ignore
        db.session.add(obj)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        db.session.refresh(obj)
        return obj

    def update(self, *, commit=True, id: Any, **data: Any) -> T:
        obj = self.get(id)
        if obj is None:
            raise ValueError(f"{self.model.__name__} {id} not found")
        for field, value in data.items():
            setattr(obj, field, value)
        db.session.add(obj)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        db.session.refresh(obj)
        return obj

    def delete(self, *, commit=True, id: Any) -> None:
        obj = self.get(id)
        if obj is None:
            return
        db.session.delete(obj)
        if commit:
            db.session.commit()
        else:
            db.session.flush()

    def count(self, **filters: Any) -> int:
        stmt = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            stmt = stmt.where(getattr(self.model, field) == value)
        return db.session.scalar(stmt)