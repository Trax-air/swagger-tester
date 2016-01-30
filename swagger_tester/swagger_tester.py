# -*- coding: utf-8 -*-

import json
import logging
import os
import requests
import time

try:
    from urllib import urlencode
except ImportError:  # Python 3
    from urllib.parse import urlencode

import connexion

from swagger_parser import SwaggerParser

logger = logging.getLogger(__name__)


def get_request_args(path, action, swagger_parser):
    """Get request args from an action and a path.

    Args:
        path: path of the action.
        action: action of the request(get, delete, post, put).
        swagger_parser: instance of SwaggerParser.

    Returns:
        A dict of args to transmit to bravado.
    """
    request_args = {}
    if path in swagger_parser.paths.keys() and action in swagger_parser.paths[path].keys():
        operation_spec = swagger_parser.paths[path][action]

        if 'parameters' in operation_spec.keys():
            for param_name, param_spec in operation_spec['parameters'].items():
                request_args[param_name] = swagger_parser.get_example_from_prop_spec(param_spec)

    return request_args


def validate_definition(swagger_parser, valid_response, response):
    """Validate the definition of the response given the given specification and body.

    Args:
        swagger_parser: instance of swagger parser.
        body: valid body answer from spec.
        response: response of the request.
    """
    # No answer
    if response is None:
        assert valid_response == ''
        return

    if valid_response == '':
        assert response is None or response == ''
        return

    # Validate output definition
    if isinstance(valid_response, list):  # Return type is a lists
        assert isinstance(response, list)
        if response:
            valid_response = valid_response[0]
            response = response[0]
        else:
            return

    # Check if there is a definition that match body and response
    assert len(set(swagger_parser.get_dict_definition(valid_response, get_list=True))
               .intersection(swagger_parser.get_dict_definition(response, get_list=True))) >= 1


def parse_parameters(url, action, path, request_args, swagger_parser):
    """Parse the swagger parameters to make a request.

    Replace var in url, make query dict, body and headers.

    Args:
        url: url of the request.
        action: HTTP action.
        path: path of the request.
        request_args: dict of args to send to the request.
        swagger_parser: instance of swagger parser.

    Returns:
        (url, body, query_params, headers)
    """
    body = None
    query_params = {}
    headers = [('Content-Type', 'application/json')]

    if path in swagger_parser.paths.keys() and action in swagger_parser.paths[path].keys():
        operation_spec = swagger_parser.paths[path][action]

        # Get body and path
        for parameter_name, parameter_spec in operation_spec['parameters'].items():
            if parameter_spec['in'] == 'body':
                body = request_args[parameter_name]
            elif parameter_spec['in'] == 'path':
                url = url.replace('{{{0}}}'.format(parameter_name), str(request_args[parameter_name]))
            elif parameter_spec['in'] == 'query':
                if isinstance(request_args[parameter_name], list):
                    query_params[parameter_name] = ','.join(request_args[parameter_name])
                else:
                    query_params[parameter_name] = str(request_args[parameter_name])
            elif parameter_spec['in'] == 'formData':
                if body is None:
                    body = {}
                body[parameter_name] = request_args[parameter_name]
                headers = [('Content-Type', 'multipart/form-data')]
    return url, body, query_params, headers


def get_url_body_from_request(action, path, request_args, swagger_parser):
    """Get the url and the body from an action, path, and request args.

    Args:
        action: HTTP action.
        path: path of the request.
        request_args: dict of args to send to the request.
        swagger_parser: instance of swagger parser.

    Returns:
        (url, body)
    """
    url = u'{0}{1}'.format(swagger_parser.base_path, path)
    url, body, query_params, headers = parse_parameters(url, action, path, request_args, swagger_parser)

    url = '{0}?{1}'.format(url, urlencode(query_params))

    try:
        body = json.dumps(body)
    except TypeError as exc:
        logger.warning(u'Cannot decode body: {0}.'.format(exc))

    return url, body, headers


def get_method_from_action(client, action):
    """Get a client method from an action.

    Args:
        client: flask client.
        aciton: action name.

    Returns:
        A flask client function.
    """
    if action == 'get':
        return client.get
    elif action == 'post':
        return client.post
    elif action == 'put':
        return client.put
    elif action == 'delete':
        return client.delete
    elif action == 'patch':
        return client.patch


def swagger_test(swagger_yaml_path=None, app_url=None, authorize_error=None, wait_between_test=False):
    """Test the given swagger api.

    Test with either a swagger.yaml path for a connexion app or with an API
    URL if you have a running API.

    Args:
        swagger_yaml_path: path of your YAML swagger file.
        app_url: URL of the swagger api.
        authorize_error: dict containing the error you don't want to raise.
                         ex: {
                            'get': {
                                '/pet/': ['404']
                            }
                         }
                         Will ignore 404 when getting a pet.
        wait_between_test: wait between tests (useful if you use ES).

    Raises:
        ValueError: In case you specify neither a swagger.yaml path or an app URL.
    """
    for _ in swagger_test_yield(swagger_yaml_path=swagger_yaml_path,
                                app_url=app_url,
                                authorize_error=authorize_error,
                                wait_between_test=wait_between_test):
        pass


def swagger_test_yield(swagger_yaml_path=None, app_url=None, authorize_error=None, wait_between_test=False):
    """Test the given swagger api. Yield the action and operation done for each test.

    Test with either a swagger.yaml path for a connexion app or with an API
    URL if you have a running API.

    Args:
        swagger_yaml_path: path of your YAML swagger file.
        app_url: URL of the swagger api.
        authorize_error: dict containing the error you don't want to raise.
                         ex: {
                            'get': {
                                '/pet/': ['404']
                            }
                         }
                         Will ignore 404 when getting a pet.
        wait_between_test: wait between tests (useful if you use Elasticsearch).

    Returns:
        Yield between each test: (action, operation)

    Raises:
        ValueError: In case you specify neither a swagger.yaml path or an app URL.
    """
    if authorize_error is None:
        authorize_error = {}

    # Init test
    if swagger_yaml_path is not None:
        app = connexion.App(__name__, port=8080, debug=True, specification_dir=os.path.dirname(os.path.realpath(swagger_yaml_path)))
        app.add_api(os.path.basename(swagger_yaml_path))
        app_client = app.app.test_client()
        swagger_parser = SwaggerParser(swagger_yaml_path, use_example=False)
    elif app_url is not None:
        app_client = requests
        swagger_parser = SwaggerParser(swagger_dict=requests.get(u'{0}/swagger.json'.format(app_url)).json(),
                                       use_example=False)
    else:
        raise ValueError('You must either specify a swagger.yaml path or an app url')

    operation_sorted = {'post': [], 'get': [], 'put': [], 'patch': [], 'delete': []}

    # Sort operation by action
    for operation, request in swagger_parser.operation.items():
        operation_sorted[request[1]].append((operation, request))

    postponed = []

    # For every operationId
    for action in ['post', 'get', 'put', 'patch', 'delete']:
        for operation in operation_sorted[action]:
            # Make request
            path = operation[1][0]
            action = operation[1][1]

            request_args = get_request_args(path, action, swagger_parser)
            url, body, headers = get_url_body_from_request(action, path, request_args, swagger_parser)

            if swagger_yaml_path is not None:
                response = get_method_from_action(app_client, action)(url, headers=headers,
                                                                      data=body)
            else:
                response = get_method_from_action(app_client, action)(u'{0}{1}'.format(app_url.replace(swagger_parser.base_path, ''), url),
                                                                      headers=dict(headers),
                                                                      data=body)

            logger.info(u'TESTING {0} {1}: {2}'.format(action.upper(), url, response.status_code))

            # Check if authorize error
            if (action in authorize_error and url in authorize_error[action] and
                    response.status_code in authorize_error[action][url]):
                yield (action, operation)
                continue

            if not response.status_code == 404:
                # Get valid request and response body
                body_req = swagger_parser.get_send_request_correct_body(path, action)
                response_spec = swagger_parser.get_request_data(path, action, body_req)

                # Get response data
                if hasattr(response, 'content'):
                    response_text = response.content
                else:
                    response_text = response.data

                # Get json
                try:
                    response_json = json.loads(response_text.decode('utf-8'))
                except (ValueError, AttributeError):
                    response_json = None

                assert response.status_code in response_spec.keys()
                assert response.status_code < 400

                validate_definition(swagger_parser, response_spec[response.status_code], response_json)

                if wait_between_test:  # Wait
                    time.sleep(2)

                yield (action, operation)
            else:
                # 404 => Postpone retry
                if {'action': action, 'operation': operation} in postponed:  # Already postponed => raise error
                    raise Exception(u'Invalid status code {0}'.format(response.status_code))

                operation_sorted[action].append(operation)
                postponed.append({'action': action, 'operation': operation})
                yield (action, operation)
                continue
