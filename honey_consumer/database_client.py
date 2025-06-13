import os
from typing import Any
from sqlmodel import Session
from sqlmodel import create_engine


import logging

logger = logging.getLogger(__name__)


class DatabaseClient:

    def __init__(self):
        database_name = os.getenv("DATABASE_NAME")
        # database_connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database_name}"
        database_connection_string = f"sqlite:///{database_name}"
        self.database_engine = create_engine(database_connection_string)
        logger.info("Database engine created with %s", database_connection_string)

    def insert_into(self, model: Any) -> bool:
        try:
            with Session(self.database_engine) as s:
                s.add(model)
                s.commit()
                return True
        except Exception as e:
            logger.error("Failed to insert model into database: %s", e, exc_info=True)
            return False
