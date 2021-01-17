import json

from handlers import ping


def json_response(response_body):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/json'
        },
        'body': json.dumps(response_body),
    }


def handle_lambda(event, context):
    print(f"request: {json.dumps(event)}")

    body = json.loads(event['body'])
    if body['type'] == 1:
        return json_response(ping.call(body))
