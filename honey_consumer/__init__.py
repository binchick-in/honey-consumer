from honey_consumer.logging_config import setup_logging

setup_logging()

import logging

logger = logging.getLogger(__name__)

logger.info("Logging was setup...")
