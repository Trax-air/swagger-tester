#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


requirements = parse_requirements('requirements.txt')
test_requirements = parse_requirements('requirements_dev.txt')

setup(
    name='swagger_tester',
    version='0.2.12',
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
