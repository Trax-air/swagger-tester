#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest

from swagger_tester import swagger_test


@pytest.mark.parametrize('example', [True, False])
def test_swagger_test(example):
    swagger_test(os.path.join(os.path.dirname(__file__), 'swagger.yaml'), use_example=example)


def test_swagger_test_app_url():
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

    swagger_test(app_url='http://petstore.swagger.io/v2',
                 authorize_error=authorize_error)
