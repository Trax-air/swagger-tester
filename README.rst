.. image:: https://travis-ci.org/Trax-air/swagger-tester.svg?branch=master
   :alt: Travis status
   :target: https://travis-ci.org/Trax-air/swagger-tester
.. image:: https://www.quantifiedcode.com/api/v1/project/8c8d73f7301242c2af0a8e12025bc4ce/badge.svg
  :target: https://www.quantifiedcode.com/app/project/8c8d73f7301242c2af0a8e12025bc4ce
  :alt: Code issues
.. image:: https://badges.gitter.im/Trax-air/swagger-tester.svg
  :alt: Join the chat at https://gitter.im/Trax-air/swagger-tester
  :target: https://gitter.im/Trax-air/swagger-tester?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
.. image:: https://www.versioneye.com/user/projects/56b4a93a0a0ff5002c85f718/badge.svg
  :alt: Dependency Status
  :target: https://www.versioneye.com/user/projects/56b4a93a0a0ff5002c85f718
.. image:: https://img.shields.io/pypi/v/swagger-tester.svg
    :target: https://pypi.python.org/pypi/swagger-tester/
.. image:: https://img.shields.io/pypi/dw/swagger-tester.svg
    :target: https://pypi.python.org/pypi/swagger-tester/

swagger-tester
==============

Swagger-tester will test automatically your swagger API. Swagger API made with connexion (https://github.com/zalando/connexion) are supported directly without running the API server. In the case you use connexion it will automatically run a test server from your swagger file.

To run the test, swagger-tester will detect every path and actions of your API. And for each, it will send a request and check if the response match the swagger file specification.

Related Libraries
-----------------
You may find related libraries to this one:

- https://github.com/Trax-air/swagger-stub: A stub you can use in your client's unit tests. All the HTTP calls to your swagger API are mocked by default. You can also add your own mocked_calls in your test functions.
- https://github.com/Trax-air/swagger-aggregator: Aggregate several swagger specs into one. Useful for your API gateways!
- https://github.com/Trax-air/swagger-parser: A helper that parses swagger specs. You can access the HTTP actions / paths and some example data

Example Usage
-------------

.. code:: python

 from swagger_tester import swagger_test

  # Define the error you authorize in your API
  # By default, every status_code over other than 1xx, 2xx or 3xx
  # will be considered as an error.
  authorize_error = {
        'post': {
            '/pet/{petId}': [200],
            '/pet': [200]
        },
        'put': {
            '/user/{username}': [200],
            '/pet': [200]
        },
        'delete': {
            '/pet/{petId}': [200],
            '/store/order/{orderId}': [200],
            '/user/{username}': [200]
        }
    }

  # Run the test with connexion
  # An AssertionError will be raise in case of error.
  swagger_test('path_to_your_swagger.yaml', authorize_error=authorize_error)

  # Or if you have a running API
  swagger_test(app_url='http://petstore.swagger.io/v2', authorize_error=authorize_error)

Documentation
-------------

More documentation is available at https://swagger-tester.readthedocs.org/en/latest/.

Setup
-----

`make install` or `pip install swagger-tester`

License
-------

swagger-tester is licensed under http://opensource.org/licenses/MIT.
