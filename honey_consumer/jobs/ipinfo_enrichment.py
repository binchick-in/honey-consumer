import os
import httpx
import asyncio

import logging

from sqlmodel import SQLModel
from sqlmodel import Session
from sqlmodel import select

from honey_consumer.database_client import DatabaseClient
from honey_consumer.models import Honey
from honey_consumer.models import IpInfo


IPINFO_KEY = os.environ["IPINFO_KEY"]
logger = logging.getLogger("honey_consumer.jobs.ipinfo_enrichment")


async def fetch_ip_info(ip_address: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.ipinfo.io/lite/{ip_address}", params={"token": IPINFO_KEY}
        )
        response.raise_for_status()
        return response


async def main():
    db_client = DatabaseClient()
    SQLModel.metadata.create_all(db_client.database_engine)
    with Session(db_client.database_engine) as sess:
        statement = (
            select(Honey.remote_address)
            .distinct()
            .outerjoin(IpInfo, Honey.remote_address == IpInfo.ip_address)
            .where(IpInfo.ip_address.is_(None))
        )
        unenriched_ips: list[str] = sess.exec(statement).all()

        logger.info("Found %d unenriched IPs", len(unenriched_ips))
        for honey_ip_address in unenriched_ips:
            try:
                logger.info("Enriching IP: %s", honey_ip_address)
                ipinfo_resp = await fetch_ip_info(honey_ip_address)
                ipinfo_data = ipinfo_resp.json()
                ipinfo_data["ip_address"] = honey_ip_address
                new_ipinfo = IpInfo.from_json_dict(ipinfo_data)
                sess.add(new_ipinfo)
                sess.commit()
                logger.info(
                    "Successfully enriched and committed IP: %s", honey_ip_address
                )
            except Exception as e:
                logger.error(
                    "Failed to enrich IP %s: %s", honey_ip_address, e, exc_info=True
                )


if __name__ == "__main__":
    asyncio.run(main())
