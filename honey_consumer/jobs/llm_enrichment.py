import asyncio
import logging
import json

from sqlmodel import SQLModel
from sqlmodel import Session
from sqlmodel import select

from ollama import chat
from ollama import AsyncClient

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


from honey_consumer.database_client import DatabaseClient
from honey_consumer.models import Honey
from honey_consumer.models import LLMDetails


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a security analyst classifying HTTP requests captured by a honeypot. Analyze the provided request data and return a JSON classification.

## Request Data Format
The request will include these fields:
- method: HTTP method (GET, POST, etc.)
- path: Request path/URI
- user_agent: User-Agent header
- query_params: Query string parameters
- headers: HTTP headers as string
- body: Request body (if POST)

## Classification Guidelines

### malicious (required)
- **high**: Clear exploit attempts with payloads (RCE, SQLi, XSS, file inclusion, etc.)
- **medium**: Suspicious reconnaissance (admin panels, config files, vulnerability probing)
- **low**: Automated scanning, crawlers, or benign activity

### type_of_exploit (null if none detected) Ensure you response with null as null type and not a string of "null" if you leave this null.
Examples: "SQL Injection", "Remote Code Execution", "Path Traversal", "XSS", "XXE", "SSRF", "Authentication Bypass", "Information Disclosure"

### target_software (null if unknown) Ensure you response with null as null type and not a string of "null" if you leave this null.
Only specify if confident based on paths/payloads. Examples: "WordPress", "Apache", "nginx", "PHPMyAdmin", "Joomla", "Spring Framework".

Respond with a raw json string and nothing else. Do not add triple back ticks to the response. Just the raw json string.

# Example Response
{
  "malicious": "high",
  "type_of_exploit": "RCE",
  "target_software": "Wordpress"
}

# Another Example Response
{
  "malicious": "low",
  "type_of_exploit": null,
  "target_software": nul
}
"""


class HTTPDetails(BaseModel):
    malicious: str = Field(...)
    type_of_exploit: str | None = Field(default=None)
    target_software: str | None = Field(defalt=None)

    @field_validator("type_of_exploit", "target_software")
    @classmethod
    def validate_string_or_none(cls, v: str | None) -> str | None:
        """The stupid LLM keeps returning these fields as strings: 'null', instead of just null (NoneType)"""
        if v is None:
            return None

        if isinstance(v, str):
            stripped = v.strip()
            if stripped.lower() == "null":
                return None
            if stripped:
                return stripped

            raise ValueError("Field must be either None, 'null', or a non-empty string")

        raise ValueError("Field must be either None or a string")


async def run_llm_inference(payload: str) -> dict[str, str]:
    response = await AsyncClient().chat(
        model="gemma3",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": payload},
        ],
        format=HTTPDetails.model_json_schema(),
    )
    return json.loads(response.message.content)


async def main():
    db_client = DatabaseClient()
    SQLModel.metadata.create_all(db_client.database_engine)

    with Session(db_client.database_engine) as sess:
        statement = (
            select(Honey)
            .outerjoin(LLMDetails, Honey.id == LLMDetails.honey_id)
            .where(LLMDetails.malicious.is_(None))
        )
        unenriched_honey = sess.exec(statement).all()
        logger.info(
            "Found %d honey records without LLM enrichment...", len(unenriched_honey)
        )
        for h in unenriched_honey:
            logger.info("Looking up id: %s", h.id)
            try:
                llm_response = await run_llm_inference(h.to_llm_context())
                logger.debug("LLM response for id %s: %s", h.id, llm_response)
                new_llm_details = LLMDetails.from_json_dict(
                    honey_id=h.id, data=llm_response
                )
                sess.add(new_llm_details)
                sess.commit()
                logger.info("Successfully enriched honey record id: %s", h.id)
            except Exception as e:
                logger.error(
                    "Failed to enrich honey record id %s: %s", h.id, e, exc_info=True
                )


if __name__ == "__main__":
    asyncio.run(main())
