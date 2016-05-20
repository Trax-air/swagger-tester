#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pip.req import parse_requirements
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [str(i.req) for i in parse_requirements('requirements.txt', session=False)]
test_requirements = [str(i.req) for i in parse_requirements('requirements_dev.txt', session=False)]

setup(
    name='swagger_tester',
    version='0.2.6',
    description="Automatically test your swagger API",
    long_description=readme + '\n\n' + history,
    author="Cyprien Guillemot",
    author_email='cyprien.guillemot@gmail.com',
    url='https://github.com/Trax-air/swagger-tester',
    packages=[
        'swagger_tester',
    ],
    package_dir={'swagger_tester':
                 'swagger_tester'},
    include_package_data=True,
    setup_requires=['pytest-runner'],
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='swagger, tester, API, REST, swagger-tester',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
