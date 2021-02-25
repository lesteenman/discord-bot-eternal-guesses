import json
from typing import Dict


class LambdaResponse:
    body: str
    status_code: int
    content_type: str

    def json(self):
        return {
            'headers': {
                'Content-Type': 'application/json'
            },
            'statusCode': self.status_code,
            'body': self.body,
        }

    @staticmethod
    def success(body: Dict):
        response = LambdaResponse()
        response.status_code = 200
        response.body = json.dumps(body)

        return response

    @staticmethod
    def unauthorized(error: str):
        response = LambdaResponse()
        response.status_code = 401
        response.body = error

        return response

    @staticmethod
    def invalid(error: str):
        response = LambdaResponse()
        response.status_code = 500
        response.body = error

        return response
