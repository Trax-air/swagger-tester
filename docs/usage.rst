=====
Usage
=====

To use Swagger Tester in a project:

.. code:: python

  from swagger_tester import swagger_test

  # Dict containing the error you don't want to raise.
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
