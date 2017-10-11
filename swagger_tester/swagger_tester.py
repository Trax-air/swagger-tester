# -*- coding: utf-8 -*-

import json
import logging
import os
import requests
import six
import time

try:
    from urllib import urlencode
except ImportError:  # Python 3
    from urllib.parse import urlencode

import connexion

from swagger_parser import SwaggerParser

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# The swagger path item object (as well as HTTP) allows for the following
# HTTP methods (http://swagger.io/specification/#pathItemObject):
_HTTP_METHODS = ['put', 'post', 'get', 'delete', 'options', 'head', 'patch']


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
    # additionalProperties do not match any definition because the keys
    # vary. we can only check the type of the values
    if 'any_prop1' in valid_response and 'any_prop2' in valid_response:
        assert swagger_parser.validate_additional_properties(valid_response, response)
        return

    # No answer
    if response is None or response == '':
        assert valid_response == '' or valid_response is None
        return

    if valid_response == '' or valid_response is None:
        assert response is None or response == ''
        return

    # Validate output definition
    if isinstance(valid_response, list):  # Return type is a list
        assert isinstance(response, list)
        if response:
            valid_response = valid_response[0]
            response = response[0]
        else:
            return

    # Not a dict and not a text
    if ((not isinstance(response, dict) or not isinstance(valid_response, dict)) and
        (not isinstance(response, (six.text_type, six.string_types)) or
            not isinstance(valid_response, (six.text_type, six.string_types)))):
        assert type(response) == type(valid_response)
    elif isinstance(response, dict) and isinstance(valid_response, dict):
        # Check if there is a definition that match body and response
        valid_definition = swagger_parser.get_dict_definition(valid_response, get_list=True)
        actual_definition = swagger_parser.get_dict_definition(response, get_list=True)
        assert len(set(valid_definition).intersection(actual_definition)) >= 1


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
        (url, body, query_params, headers, files)
    """
    body = None
    query_params = {}
    files = {}
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

                if (isinstance(request_args[parameter_name], tuple) and
                        hasattr(request_args[parameter_name][0], 'read')):
                    files[parameter_name] = (request_args[parameter_name][1],
                                             request_args[parameter_name][0])
                else:
                    body[parameter_name] = request_args[parameter_name]

                # The first header is always content type, so just replace it so we don't squash custom headers
                headers[0] = ('Content-Type', 'multipart/form-data')
            elif parameter_spec['in'] == 'header':
                header_value = request_args.get(parameter_name)
                header_value = header_value or parameter_spec.get('default', '')
                headers += [(parameter_spec['name'], str(header_value))]
    return url, body, query_params, headers, files


def get_url_body_from_request(action, path, request_args, swagger_parser):
    """Get the url and the body from an action, path, and request args.

    Args:
        action: HTTP action.
        path: path of the request.
        request_args: dict of args to send to the request.
        swagger_parser: instance of swagger parser.

    Returns:
        url, body, headers, files
    """
    url, body, query_params, headers, files = parse_parameters(path, action, path, request_args, swagger_parser)

    url = '{0}?{1}'.format(url, urlencode(query_params))

    if ('Content-Type', 'multipart/form-data') not in headers:
        try:
            if body:
                body = json.dumps(body)
        except TypeError as exc:
            logger.warning(u'Cannot decode body: {0}.'.format(repr(exc)))
    else:
        headers.remove(('Content-Type', 'multipart/form-data'))

    return url, body, headers, files


def get_method_from_action(client, action):
    """Get a client method from an action.

    Args:
        client: flask client.
        aciton: action name.

    Returns:
        A flask client function.
    """
    error_msg = "Action '{0}' is not recognized; needs to be one of {1}.".format(action, str(_HTTP_METHODS))
    assert action in _HTTP_METHODS, error_msg

    return client.__getattribute__(action)


def swagger_test(swagger_yaml_path=None, app_url=None, authorize_error=None,
                 wait_time_between_tests=0, use_example=True, dry_run=False,
                 extra_headers={}):
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
        wait_time_between_tests: an number that will be used as waiting time between tests [in seconds].
        use_example: use example of your swagger file instead of generated data.
        dry_run: don't actually execute the test, only show what would be sent
        extra_headers: additional headers you may want to send for all operations

    Raises:
        ValueError: In case you specify neither a swagger.yaml path or an app URL.
    """
    for _ in swagger_test_yield(swagger_yaml_path=swagger_yaml_path,
                                app_url=app_url,
                                authorize_error=authorize_error,
                                wait_time_between_tests=wait_time_between_tests,
                                use_example=use_example,
                                dry_run=dry_run,
                                extra_headers=extra_headers):
        pass


def swagger_test_yield(swagger_yaml_path=None, app_url=None, authorize_error=None,
                       wait_time_between_tests=0, use_example=True, dry_run=False,
                       extra_headers={}):
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
        wait_time_between_tests: an number that will be used as waiting time between tests [in seconds].
        use_example: use example of your swagger file instead of generated data.
        dry_run: don't actually execute the test, only show what would be sent
        extra_headers: additional headers you may want to send for all operations

    Returns:
        Yield between each test: (action, operation)

    Raises:
        ValueError: In case you specify neither a swagger.yaml path or an app URL.
    """
    if authorize_error is None:
        authorize_error = {}

    # Init test
    if swagger_yaml_path is not None and app_url is not None:
        app_client = requests
        swagger_parser = SwaggerParser(swagger_yaml_path, use_example=use_example)
    elif swagger_yaml_path is not None:
        specification_dir = os.path.dirname(os.path.realpath(swagger_yaml_path))
        app = connexion.App(__name__, port=8080, debug=True, specification_dir=specification_dir)
        app.add_api(os.path.basename(swagger_yaml_path))
        app_client = app.app.test_client()
        swagger_parser = SwaggerParser(swagger_yaml_path, use_example=use_example)
    elif app_url is not None:
        app_client = requests
        remote_swagger_def = requests.get(u'{0}/swagger.json'.format(app_url)).json()
        swagger_parser = SwaggerParser(swagger_dict=remote_swagger_def, use_example=use_example)
    else:
        raise ValueError('You must either specify a swagger.yaml path or an app url')

    print("Starting testrun against {0} or {1} using examples: "
          "{2}".format(swagger_yaml_path, app_url, use_example))

    operation_sorted = {method: [] for method in _HTTP_METHODS}

    # Sort operation by action
    operations = swagger_parser.operation.copy()
    operations.update(swagger_parser.generated_operation)
    for operation, request in operations.items():
        operation_sorted[request[1]].append((operation, request))

    postponed = []

    # For every operationId
    for action in _HTTP_METHODS:
        for operation in operation_sorted[action]:
            # Make request
            path = operation[1][0]
            action = operation[1][1]
            client_name = getattr(app_client, '__name__', 'FlaskClient')

            request_args = get_request_args(path, action, swagger_parser)
            url, body, headers, files = get_url_body_from_request(action, path, request_args, swagger_parser)

            logger.info(u'TESTING {0} {1}'.format(action.upper(), url))

            # Add any extra headers specified by the user
            headers.extend([(key, value)for key, value in extra_headers.items()])

            if swagger_yaml_path is not None and app_url is None:
                if dry_run:
                    logger.info("\nWould send %s to %s with body %s and headers %s" %
                                (action.upper(), url, body, headers))
                    continue
                response = get_method_from_action(app_client, action)(url, headers=headers, data=body)
            else:
                if app_url.endswith(swagger_parser.base_path):
                    base_url = app_url[:-len(swagger_parser.base_path)]
                else:
                    base_url = app_url
                full_path = u'{0}{1}'.format(base_url, url)
                if dry_run:
                    logger.info("\nWould send %s to %s with body %s and headers %s" %
                                (action.upper(), full_path, body, headers))
                    continue
                response = get_method_from_action(app_client, action)(full_path,
                                                                      headers=dict(headers),
                                                                      data=body,
                                                                      files=files)

            logger.info(u'Using {0}, got status code {1} for ********** {2} {3}'.format(
                client_name, response.status_code, action.upper(), url))

            # Check if authorize error
            if (action in authorize_error and path in authorize_error[action] and
                    response.status_code in authorize_error[action][path]):
                logger.info(u'Got expected authorized error on {0} with status {1}'.format(url, response.status_code))
                yield (action, operation)
                continue

            if response.status_code is not 404:
                # Get valid request and response body
                body_req = swagger_parser.get_send_request_correct_body(path, action)

                try:
                    response_spec = swagger_parser.get_request_data(path, action, body_req)
                except (TypeError, ValueError) as exc:
                    logger.warning(u'Error in the swagger file: {0}'.format(repr(exc)))
                    continue

                # Get response data
                if hasattr(response, 'content'):
                    response_text = response.content
                else:
                    response_text = response.data

                # Convert to str
                if hasattr(response_text, 'decode'):
                    response_text = response_text.decode('utf-8')

                # Get json
                try:
                    response_json = json.loads(response_text)
                except ValueError:
                    response_json = response_text

                if response.status_code in response_spec.keys():
                    validate_definition(swagger_parser, response_spec[response.status_code], response_json)
                elif 'default' in response_spec.keys():
                    validate_definition(swagger_parser, response_spec['default'], response_json)
                else:
                    raise AssertionError('Invalid status code {0}. Expected: {1}'.format(response.status_code,
                                                                                         response_spec.keys()))

                if wait_time_between_tests > 0:
                    time.sleep(wait_time_between_tests)

                yield (action, operation)
            else:
                # 404 => Postpone retry
                if {'action': action, 'operation': operation} in postponed:  # Already postponed => raise error
                    raise Exception(u'Invalid status code {0}'.format(response.status_code))

                operation_sorted[action].append(operation)
                postponed.append({'action': action, 'operation': operation})
                yield (action, operation)
                continue
