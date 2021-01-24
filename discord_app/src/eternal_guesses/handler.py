import json
import logging
from typing import Dict

import authorizer
import router

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def handle_lambda(event, context) -> Dict:
    log.debug(f"request: {json.dumps(event)}")
    log.info(f"body:\n{event['body']}'")
    log.info(f"headers:\n{event['headers']}'")

    result, response = authorizer.authorize(event)
    if result == authorizer.AuthorizationResult.PASS:
        body = json.loads(event['body'])
        response = router.route(body)

    return response.json()
