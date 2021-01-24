import logging
from typing import Dict


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def call(body: Dict) -> Dict:
    return {"type": 1}
