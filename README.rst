.. image:: https://travis-ci.org/Trax-air/swagger-tester.svg?branch=master
   :alt: Travis status
   :target: https://travis-ci.org/Trax-air/swagger-tester

swagger-tester
==============

Swagger-tester will test automatically your swagger API. Currently only swagger API made with connexion (https://github.com/zalando/connexion) are supported.

To run the test, swagger-tester will start a flask test server of your API. Then it will detect every path and actions of your API. And for each, it will send a request and check if the response match the swagger file specification.

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

  # Run the test
  # An AssertionError will be raise in case of error.
  swagger_test('path_to_your_swagger.yaml', authorize_error=authorize_error)

Documentation
-------------

More documentation is available at https://swagger-tester.readthedocs.org/en/latest/.

Setup
-----

`make install` or `pip install swagger-tester`

License
-------

swagger-tester is licensed under http://opensource.org/licenses/GPL-3.0.
