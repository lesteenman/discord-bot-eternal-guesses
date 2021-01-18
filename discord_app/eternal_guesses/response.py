import json
from typing import Dict


def success(response_body: Dict) -> Dict:
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/json'
        },
        'body': json.dumps(response_body),
    }


def invalid(error: str) -> Dict:
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'text/json'
        },
        'body': error,
    }


def unauthorized() -> Dict:
    return {
        'statusCode': 401,
        'headers': {
            'Content-Type': 'text/json'
        },
    }
