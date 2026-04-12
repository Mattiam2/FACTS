from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar

from sqlmodel import SQLModel, select, func

from ebsi_sim.core.db import db

T = TypeVar("T", bound=SQLModel)


class Repository(ABC, Generic[T]):
    """
    Abstract base class for a repository pattern.

    This class defines the interface for a repository, designed to handle CRUD
    (Create, Read, Update, Delete) operations and enable data manipulation. It
    enforces the implementation of these operations in any subclass and allows
    for interaction with underlying data sources, abstracting their details
    and providing a unified structure for data access.
    """

    @abstractmethod
    def get(self, id: Any) -> T | None: ...

    @abstractmethod
    def list(self, *, offset=0, limit=100,
             order_by: str | None = None, **filters) -> list[T]: ...

    @abstractmethod
    def create(self, **data: Any) -> T: ...

    @abstractmethod
    def update(self, id: Any, **data: Any) -> T: ...

    @abstractmethod
    def delete(self, id: Any) -> None: ...


class BaseRepository(Repository[T]):
    """
    BaseRepository serves as a generic repository class to manage operations such as
    retrieval, creation, updating, and deletion of database entities.

    :ivar model: The SQLModel model class managed by the repository.
    :type model: Type[T]
    """
    model: Type[T]

    def __init__(self, model: Type[T]):
        self.model = model

    def get(self, id: Any) -> T | None:
        """
        Retrieves an instance of the specified model using its unique identifier.

        :param id: Unique identifier of the instance to retrieve
        :type id: Any
        :return: An instance of the specified entity if found, otherwise None
        :rtype: T | None
        """
        return db.session.get(self.model, id)

    def list(self, *, offset: int = 0, limit: int = 100, order_by: str | None = None, **filters) -> list[T]:
        """
        Fetches a list of records from the database based on the specified parameters.

        :param offset: The starting position of the records to fetch. Default is 0.
        :type offset: int
        :param limit: The maximum number of records to fetch. Default is 100.
        :type limit: int
        :param order_by: The field by which to order the results. Default is None.
        :type order_by: str | None
        :param filters: Key-value pairs representing filter criteria to apply.
        :type filters: Any
        :return: A list of retrieved records of the specified type.
        :rtype: list[T]
        """
        stmt = select(self.model)
        for field, value in filters.items():
            if value is not None:
                stmt = stmt.where(getattr(self.model, field) == value)
        if order_by:
            stmt = stmt.order_by(getattr(self.model, order_by))
        stmt = stmt.offset(offset).limit(limit)
        return list(db.session.scalars(stmt))

    def create(self, *, commit=False, **data) -> T:
        """
        Create a new instance of the specified model using the data provided.

        :param commit: Determines whether the new object is immediately committed to the
            database. Defaults to True.
        :type commit: bool

        :param data: Key-value pairs with data to be used to initialize the new object.
        :type data: Any
        :return: The object created and persisted into the database.
        :rtype: T
        """
        obj = self.model(**data)
        db.session.add(obj)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        return obj

    def update(self, *, commit=False, id: Any, **data) -> T:
        """
        Update an existing object in the database.

        :param commit: A boolean indicating whether to commit the changes to the database.
                       If False, only flush the changes. Defaults to False.
        :type commit: bool
        :param id: The unique identifier of the object to be updated.
        :type id: Any
        :param data: Key-value pairs representing the fields and their new values to update
                     on the retrieved object.
        :type data: Any
        :return: The updated object.
        :rtype: T
        :raises ValueError: If the object with the given identifier is not found in the database.
        """
        obj = self.get(id)
        if obj is None:
            raise ValueError(f"{self.model.__name__} {id} not found")
        for field, value in data.items():
            setattr(obj, field, value)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        return obj

    def delete(self, *, commit=False, id: Any) -> None:
        """
        Deletes an object from the database using its identifier.

        :param commit: Determines whether to commit the deletion immediately. Defaults to False.
        :type commit: bool
        :param id: The identifier of the object to be deleted.
        :type id: Any
        :return: None
        """
        obj = self.get(id)
        if obj is None:
            return
        db.session.delete(obj)
        if commit:
            db.session.commit()
        else:
            db.session.flush()

    def count(self, **filters) -> int:
        """
        Counts the total number of entries in the database model that match the given
        filter criteria.

        :param filters: Key-value pairs representing filter criteria to apply.
        :type filters: Any
        :return: The total number of entries in the database model matching the
            provided filters.
        :rtype: int
        """
        stmt = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            if value is not None:
                stmt = stmt.where(getattr(self.model, field) == value)
        return db.session.scalar(stmt)
