from sqlmodel import SQLModel

from facts.src.core.db import engine
from facts.src.core.exceptions import FACTSDatabaseError


def create_db_and_tables():
    """
    Creates the database and all associated tables.

    :return: None
    """
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print(f"Error creating tables")
        raise FACTSDatabaseError(f"Error creating tables")
