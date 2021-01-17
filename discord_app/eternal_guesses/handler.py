import json

from eternal_guesses import discord_router


def handle_lambda(event, context):
    print('request: {}'.format(json.dumps(event)))

    response = discord_router.handle(json.loads(event['body']))

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello, CDK! You have hit {}\n'.format(event['path'])
    }
