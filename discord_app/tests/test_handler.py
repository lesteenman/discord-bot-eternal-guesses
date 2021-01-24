import json
from unittest.mock import patch

import handler
from authorizer import AuthorizationResult
from model.response import Response


@patch('authorizer.authorize')
@patch('router.route')
def test_authorized_request(mock_router, mock_authorize):
    # Given
    mock_authorize.return_value = (AuthorizationResult.PASS, None)
    mock_router.return_value = Response.success({'response': 'mocked'})

    body = {'type': 1}
    event = {
        'body': json.dumps(body),
        'headers': {
            'x-signature-ed25519': '',
            'x-signature-timestamp': '',
        }
    }
    context = {}

    # When
    response = handler.handle_lambda(event, context)

    # Then
    assert response['statusCode'] == 200

    mock_router.assert_called_with(body)
    assert json.loads(response['body']) == {'response': 'mocked'}


@patch('authorizer.authorize')
def test_unauthorized_request(mock_authorize):
    # Given
    mock_authorize.return_value = (AuthorizationResult.FAIL, Response.unauthorized("key does not check out"))

    body = {'type': 1}
    event = {
        'body': json.dumps(body),
        'headers': {
            'x-signature-ed25519': '',
            'x-signature-timestamp': '',
        }
    }
    context = {}

    # When
    response = handler.handle_lambda(event, context)

    # Then
    assert response['statusCode'] == 401
