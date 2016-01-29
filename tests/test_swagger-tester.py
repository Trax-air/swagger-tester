#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from swagger_tester import swagger_test


def test_swagger_test():
    swagger_test(os.path.join(os.path.dirname(__file__), 'swagger.yaml'))
