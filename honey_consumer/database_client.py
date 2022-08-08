import os

from sqlmodel import Session
from sqlmodel import create_engine

from honey_consumer.exceptions import NoCredsFound
from honey_consumer.models import Honey


class DatabaseClient:

    def __init__(self):
        host = os.getenv("DATABASE_HOST")
        user = os.getenv("DATABASE_USER")
        password = os.getenv("DATABASE_PASSWORD")
        database_name = os.getenv("DATABASE_NAME")

        if not all([host, user, password, database_name]):
            raise NoCredsFound("MySQL Creds")

        database_connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database_name}"
        self.database_engine = create_engine(database_connection_string, echo=True)

    def insert_into(self, model: Honey) -> bool:
        with Session(self.database_engine) as s:
            s.add(model)
            s.commit()
            return True