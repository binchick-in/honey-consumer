from typing import Optional

import datetime
import json

from sqlmodel import SQLModel
from sqlmodel import Field

from sqlalchemy import Column
from sqlalchemy import TEXT


class Honey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created: datetime.datetime
    honey_pot_name: Optional[str] = Field(nullable=True)
    time: Optional[str] = Field(nullable=True)
    host: Optional[str] = Field(nullable=True)
    method: Optional[str] = Field(nullable=True)
    path: Optional[str] = Field(nullable=True, sa_column=Column(TEXT))
    remote_address: Optional[str] = Field(nullable=True)
    user_agent: Optional[str] = Field(nullable=True, sa_column=Column(TEXT))
    query_params: Optional[str] = Field(nullable=True, sa_column=Column(TEXT))
    headers: Optional[str] = Field(nullable=True, sa_column=Column(TEXT))
    body: Optional[str] = Field(nullable=True, sa_column=Column(TEXT))

    def to_json(self) -> str:
        return json.dumps(self.__dict__)
