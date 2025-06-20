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


logger = logging.getLogger("honey_consumer.jobs.llm_enrichement")

SYSTEM_PROMPT = """
You are a security analyst classifying HTTP requests captured by a honeypot. Analyze the provided request data **strictly based on its content** and return a JSON classification.

## Request Data Format
The request will include these fields:
- method: HTTP method (GET, POST, HEAD, etc.)
- path: Request path/URI
- user_agent: User-Agent header
- query_params: Query string parameters (JSON object)
- headers: HTTP headers as string (JSON string)
- body: Request body (if POST, PUT, etc.)

## Classification Guidelines

### malicious (required)
Classify the overall maliciousness level based on the request's characteristics:
- **high**: Requests containing clear, active exploit payloads (e.g., SQL injection syntax, command execution attempts, specific cross-site scripting vectors, path traversal sequences, deserialization payloads, etc.) designed to compromise or manipulate the target system.
- **medium**: Suspicious reconnaissance activities such as scanning for administrative interfaces, configuration files, common vulnerability paths (like `/admin`, `/setup.php`, `/config.json`, specific known vulnerable script paths), directory listing attempts, or automated generic probing **without specific exploit payloads**.
- **low**: Automated scanning by legitimate crawlers (search engines, security researchers identified by User-Agent and behavior), benign checks, or other non-malicious activity.

### type_of_exploit (null if none detected)
Identify the specific type of exploit **ONLY if a clear, identifiable exploit payload or technique is present *within the request data* (path, query parameters, body, or headers)**. Do not guess the exploit type based solely on the target path if no payload is present.
Ensure you respond with `null` as the JSON null type and not a string of "null" if you leave this null.
Examples: "SQL Injection", "Cross-Site Scripting", "Remote Code Execution", "Command Injection", "Path Traversal", "Directory Traversal", "Server-Side Request Forgery", "Information Disclosure", "Authentication Bypass", "Broken Access Control", "XML External Entity", "File Inclusion", "Deserialization".

### target_software (null if unknown)
Identify the likely target software **ONLY if highly confident** based on specific paths, payloads, or headers characteristic of certain software or frameworks.
Ensure you respond with `null` as the JSON null type and not a string of "null" if you leave this null.
Examples: "WordPress", "Apache", "nginx", "PHPMyAdmin", "Joomla", "Spring Framework", "Jenkins", "Struts", "IIS".

Respond with a raw json string and nothing else. Do not add triple back ticks to the response. Just the raw json string.

# Example Response for Active Exploit
{
  "malicious": "high",
  "type_of_exploit": "SQL Injection",
  "target_software": "WordPress"
}

# Example Response for Reconnaissance/Probing
{
  "malicious": "medium",
  "type_of_exploit": null,
  "target_software": "PHPMyAdmin"
}

# Another Example Response for Low Maliciousness
{
  "malicious": "low",
  "type_of_exploit": null,
  "target_software": null
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
