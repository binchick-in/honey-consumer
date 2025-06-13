from __future__ import annotations

from typing import Optional
from typing import Any
import datetime
import json

from sqlmodel import SQLModel
from sqlmodel import Field
from sqlmodel import Relationship
from sqlalchemy.orm import Mapped


from sqlalchemy import Column
from sqlalchemy import TEXT


class Honey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created: datetime.datetime
    honey_pot_name: Optional[str] = Field(nullable=True)
    time: Optional[str] = Field(nullable=True)
    host: Optional[str] = Field(nullable=True)
    method: Optional[str] = Field(nullable=True)
    path: Optional[str] = Field(sa_column=Column(TEXT))
    remote_address: Optional[str] = Field(nullable=True)
    user_agent: Optional[str] = Field(sa_column=Column(TEXT))
    query_params: Optional[str] = Field(sa_column=Column(TEXT))
    headers: Optional[str] = Field(sa_column=Column(TEXT))
    body: Optional[str] = Field(sa_column=Column(TEXT))

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def to_llm_context(self) -> str:
        return f"""Method: {self.method}
Path: {self.path}
User-Agent: {self.user_agent}
Query Parameters: {self.query_params}
Header: {self.headers}
Body: {self.body}"""


class LLMDetails(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    honey_id: int = Field(foreign_key="honey.id")
    malicious: str | None = Field(default=None, nullable=True)
    type_of_exploit: str | None = Field(default=None, nullable=True)
    target_software: str | None = Field(default=None, nullable=True)

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json_dict(cls, *, honey_id: id, data: dict[str, Any]) -> LLMDetails:
        return cls(
            honey_id=honey_id,
            malicious=data.get("malicious"),
            type_of_exploit=data.get("type_of_exploit"),
            target_software=data.get("target_software"),
        )


class IpInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ip_address: Optional[str] = Field(nullable=True)
    asn: Optional[str] = Field(nullable=True)
    as_name: Optional[str] = Field(nullable=True)
    as_domain: Optional[str] = Field(nullable=True)
    country_code: Optional[str] = Field(nullable=True)
    country: Optional[str] = Field(nullable=True)
    continent_code: Optional[str] = Field(nullable=True)
    continent: Optional[str] = Field(nullable=True)
    created: datetime.datetime

    def to_json(self) -> str:
        import json

        return json.dumps(self.__dict__)

    @classmethod
    def from_json_dict(cls, data: dict[str, Any]) -> IpInfo:
        return cls(
            ip_address=data.get("ip_address"),
            asn=data.get("asn"),
            as_name=data.get("as_name"),
            as_domain=data.get("as_domain"),
            country_code=data.get("country_code"),
            country=data.get("country"),
            continent_code=data.get("continent_code"),
            continent=data.get("continent"),
            created=datetime.datetime.now(datetime.timezone.utc),
        )
