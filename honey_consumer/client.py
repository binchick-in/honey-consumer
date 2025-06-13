import os
import json
import datetime
import logging

from sqlmodel import SQLModel

from google.cloud import pubsub_v1

from honey_consumer.models import Honey
from honey_consumer.database_client import DatabaseClient


logger = logging.getLogger(__name__)
database = DatabaseClient()


class NoCredsFound(Exception): ...


class HoneyClient:
    def __init__(self):
        svc_creds = os.getenv("GOOGLE_SERVICE_JSON")
        sub_name = os.getenv("GOOGLE_PUB_SUBSCRIPTION_NAME", "honey-sub")

        if not svc_creds:
            raise NoCredsFound
        creds = json.loads(svc_creds, strict=False)

        self._project_name = creds.get("project_id")
        self._subscriber_client = pubsub_v1.SubscriberClient.from_service_account_info(
            creds
        )
        self._subscription_name = self._subscriber_client.subscription_path(
            self._project_name, sub_name
        )

    def process_task(self, task):
        logger.debug("Received task: %s", task)
        logger.info("Task data: %s", task.data)
        logger.debug("Task attributes: %s", task.attributes)
        deserialized_task = json.loads(task.data.decode())
        honey = Honey(**deserialized_task)
        honey.created = datetime.datetime.today()
        honey.query_params = json.dumps(deserialized_task.get("query_params"))
        honey.headers = json.dumps(deserialized_task.get("headers"))
        honey.honey_pot_name = task.attributes.get("hostname")
        database.insert_into(honey)
        task.ack()

    def listen(self):
        logger.info("Starting Honey Consumer...")
        SQLModel.metadata.create_all(database.database_engine)
        with self._subscriber_client as subscriber:
            stream = subscriber.subscribe(self._subscription_name, self.process_task)
            try:
                logger.info("Subscriber stream result: %s", stream.result())
            except KeyboardInterrupt:
                stream.cancel()
