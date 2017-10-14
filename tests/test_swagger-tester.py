#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from swagger_tester import swagger_test

import connexion
from multiprocessing import Process


class ConnexionProcess(Process):
    def run(self):
        self.conn = connexion.App(
            'tests',
            debug=True,
            specification_dir=os.path.dirname(__file__)
        )
        self.conn.add_api('swagger.yaml')
        self.conn.app.run(port=8080)

    def start(self):
        Process.start(self)

        import time
        time.sleep(3)

    def terminate(self):
        Process.terminate(self)
        Process.join(self)


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
swagger_io_url = 'http://localhost:8080/v2'


def test_swagger_test_use_example():
    swagger_test(swagger_yaml_path, use_example=True)


def test_swagger_test_dont_use_example():
    swagger_test(swagger_yaml_path, use_example=False)


def test_swagger_test_extra_headers():
    swagger_test(swagger_yaml_path, extra_headers={'X-Header': 'Value'})


def test_swagger_test_specify_app_url_use_example():
    conn = ConnexionProcess()
    conn.start()
    swagger_test(app_url=swagger_io_url,
                 authorize_error=authorize_error,
                 use_example=True)
    conn.terminate()


def test_issue_51_fixed():
    conn = ConnexionProcess()
    conn.start()
    swagger_test(app_url='http://v2@localhost:8080/v2',
                 authorize_error=authorize_error)
    conn.terminate()


def test_swagger_test_specify_app_url_dont_use_example():
    conn = ConnexionProcess()
    conn.start()
    swagger_test(app_url=swagger_io_url,
                 authorize_error=authorize_error,
                 use_example=False)
    conn.terminate()
