#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import socket
import threading

import connexion

from swagger_tester import swagger_test


def test_swagger_test():
    swagger_test(os.path.join(os.path.dirname(__file__), 'swagger.yaml'))


def get_open_port():
    """Get an open port on localhost"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def test_swagger_test_app_url():
    port = get_open_port()
    swagger_yaml_path = os.path.join(os.path.dirname(__file__), 'swagger.yaml')

    app = connexion.App(__name__, port=port, specification_dir=os.path.dirname(os.path.realpath(swagger_yaml_path)))
    app.add_api(os.path.basename(swagger_yaml_path))
    server = threading.Thread(None, app.run)
    server.daemon = True
    server.start()

    swagger_test(app_url='http://localhost:{0}/v2'.format(port))
