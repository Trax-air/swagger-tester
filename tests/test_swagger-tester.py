#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from swagger_tester import swagger_test


swagger_yaml_path = os.path.join(os.path.dirname(__file__), 'swagger.yaml')
authorize_error = {
    'post': {
        '/v2/pet/{petId}': [200],
        '/v2/pet': [200]
    },
    'put': {
        '/v2/user/{username}': [200],
        '/v2/pet': [200]
    },
    'delete': {
        '/v2/pet/{petId}': [200],
        '/v2/store/order/{orderId}': [200],
        '/v2/user/{username}': [200]
    }
}
swagger_io_url = 'http://petstore.swagger.io/v2'


def test_swagger_test_use_example():
    swagger_test(swagger_yaml_path, use_example=True)


def test_swagger_test_dont_use_example():
    swagger_test(swagger_yaml_path, use_example=False)


def test_swagger_test_specify_app_url_use_example():
    swagger_test(app_url=swagger_io_url,
                 authorize_error=authorize_error,
                 use_example=True)


def test_swagger_test_specify_app_url_dont_use_example():
    swagger_test(app_url=swagger_io_url,
                 authorize_error=authorize_error,
                 use_example=False)
