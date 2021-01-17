from typing import Dict

from eternal_guesses.views import ping


def handle(body: Dict):
    if body['type'] == 1:
        return ping.call(body)
