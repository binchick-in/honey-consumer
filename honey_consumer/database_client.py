import os
from typing import Any
from sqlmodel import Session
from sqlmodel import create_engine


class DatabaseClient:

    def __init__(self):
        database_name = os.getenv("DATABASE_NAME")
        # database_connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database_name}"
        database_connection_string = f"sqlite:///{database_name}"
        self.database_engine = create_engine(database_connection_string, echo=True)

    def insert_into(self, model: Any) -> bool:
        with Session(self.database_engine) as s:
            s.add(model)
            s.commit()
            return True
