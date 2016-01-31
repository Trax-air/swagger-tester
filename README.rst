.. image:: https://travis-ci.org/Trax-air/swagger-tester.svg?branch=master
   :alt: Travis status
   :target: https://travis-ci.org/Trax-air/swagger-tester

swagger-tester
==============

Swagger-tester will test automatically your swagger API. Swagger API made with connexion (https://github.com/zalando/connexion) are supported directly without running the API server. In the case you use connexion it will automatically run a test server from your swagger file.

To run the test, swagger-tester will detect every path and actions of your API. And for each, it will send a request and check if the response match the swagger file specification.

Example Usage
-------------

.. code:: python

 from swagger_tester import swagger_test

  # Define the error you authorize in your API
  # By default, every status_code over other than 1xx, 2xx or 3xx
  # will be considered as an error.
  authorize_error = {
    'get': {
      '/pet/': ['400', '404']
    }
  }

  # Run the test with connexion
  # An AssertionError will be raise in case of error.
  swagger_test('path_to_your_swagger.yaml', authorize_error=authorize_error)

  # Or if you have a running API on http://localhost:8080/v1
  swagger_test(app_url='http://localhost:8080/v1', authorize_error=authorize_error)

Documentation
-------------

More documentation is available at https://swagger-tester.readthedocs.org/en/latest/.

Setup
-----

`make install` or `pip install swagger-tester`

License
-------

swagger-tester is licensed under http://opensource.org/licenses/MIT.
