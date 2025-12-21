from typing import Any, Generic, Iterable, Type, TypeVar
from abc import ABC, abstractmethod
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
             order_by: str | None = None, **filters: Any) -> list[T]: ...
    @abstractmethod
    def create(self, **data: Any) -> T: ...
    @abstractmethod
    def update(self, id: Any, **data: Any) -> T: ...
    @abstractmethod
    def delete(self, id: Any) -> None: ...


class BaseRepository(Repository[T]):
    """
    BaseRepository serves as a generic repository class to manage operations such as
    retrieval, creation, updating, and deletion of entities tied to a database model.

    This class provides reusable database operations, making it a foundation class for
    repository implementations. It interacts with SQLAlchemy sessions and query APIs
    to perform CRUD operations efficiently.

    :ivar model: The SQLAlchemy model class managed by the repository.
    :type model: Type[T]
    """

    def __init__(self, model: Type[T]):
        self.model = model

    def get(self, id: Any) -> T | None:
        """
        Retrieves an instance of the specified model using its unique identifier.

        :param id: Unique identifier of the model instance to retrieve
        :type id: Any
        :return: An instance of the specified model if found, otherwise None
        :rtype: T | None
        """
        return db.session.get(self.model, id)

    def list(self, *, offset=0, limit=100, order_by=None, **filters: Any) -> list[T]:
        """
        Fetches a list of records from the database based on the specified parameters. The method
        retrieves records starting from the given offset, limits the total number of records
        retrieved, and allows ordering and filtering of the results based on specified fields.

        :param offset: The starting position of the records to fetch. Default is 0.
        :type offset: int
        :param limit: The maximum number of records to fetch. Default is 100.
        :type limit: int
        :param order_by: The field by which to order the results. Default is None, meaning no specific
                         ordering.
        :type order_by: str or None
        :param filters: A dictionary of fields and their values used to filter the results. Filters are
                        applied based on equality checks.
        :type filters: Any
        :return: A list of retrieved records of the specified type.
        :rtype: list[T]
        """
        stmt = select(self.model)
        for field, value in filters.items():
            stmt = stmt.where(getattr(self.model, field) == value)
        if order_by:
            stmt = stmt.order_by(getattr(self.model, order_by))
        stmt = stmt.offset(offset).limit(limit)
        return list(db.session.scalars(stmt))

    def create(self, *, commit=True, **data: Any) -> T:
        """
        Create a new instance of the specified model using the data provided. The method
        performs a database operation to persist the newly created object. If `commit`
        is True, the object is immediately committed to the database; otherwise, the
        changes are only flushed.

        :param commit: Determines whether the new object is immediately committed to the
            database. Defaults to True.
            - True: Commits the new object to the database.
            - False: Flushes the changes to allow further modifications before committing.
        :type commit: bool

        :param data: Arbitrary keyword arguments providing the data to instantiate the
            model object. These arguments are used to populate the fields of the model
            according to its schema or structure.
        :return: The object created and persisted into the database.
        :rtype: T
        """
        obj = self.model(**data)  # type: ignore
        db.session.add(obj)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        db.session.refresh(obj)
        return obj

    def update(self, *, commit=True, id: Any, **data: Any) -> T:
        """
        Update an existing object in the database. This method retrieves the object by its
        identifier, updates its attributes with provided data, and either commits or
        flushes the changes based on the `commit` flag.

        :param commit: A boolean indicating whether to commit the changes to the database.
                       If False, only flush the changes. Defaults to True.
        :type commit: bool
        :param id: The unique identifier of the object to be updated.
        :type id: Any
        :param data: Key-value pairs representing the fields and their new values to update
                     on the retrieved object. Additional keyword arguments are applied as updates.
        :type data: dict
        :return: The updated object.
        :rtype: T
        :raises ValueError: If the object with the given identifier is not found in the database.
        """
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
        """
        Deletes an object from the database using its identifier. If the identifier does not
        correspond to any existing object, the function exits without performing any operation.
        The deletion can either be committed immediately to the database or left for a later
        explicit commit based on the 'commit' flag.

        :param commit: Determines whether to commit the deletion immediately. Defaults to True.
                       If False, the deletion will only be flushed to the database session.
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

    def count(self, **filters: Any) -> int:
        """
        Counts the total number of entries in the database model that match the given
        filter criteria. The filtering is dynamically applied based on the field-value
        pairs passed as keyword arguments.

        :param filters: A set of keyword arguments where the key represents the name
            of the field in the model, and the value represents the value that the
            field should be compared to.
        :type filters: Any
        :return: The total number of entries in the database model matching the
            provided filters.
        :rtype: int
        """
        stmt = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            stmt = stmt.where(getattr(self.model, field) == value)
        return db.session.scalar(stmt)