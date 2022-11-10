import pprint
from datetime import datetime
from typing import Dict

from aws_xray_sdk.core import patch_all
from loguru import logger

from eternal_guesses import event_handler

discord_event_handler = None

patch_all()


def handle_lambda(event, context) -> Dict:
    logger.debug(f"body: {pprint.pformat(event['body'])}")
    logger.debug(f"headers:{pprint.pformat(event['headers'])}")
    logger.debug(f"context:{pprint.pformat(context)}")

    return event_handler.handle(event)


# Call here to prewarm
def prewarm():
    start = datetime.now()
    event_handler.get_event_handler()
    duration = datetime.now() - start
    logger.info(f"get_event_handler duration: {duration.total_seconds()}")


prewarm()
