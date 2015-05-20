
import urllib
import tornado
from tornado.testing import *

class SwiftDiffTestCaseCollate(AsyncTestCase):

    @tornado.testing.gen_test

    def test_http_fetch(self):

        client = AsyncHTTPClient(self.io_loop)

        post_data = { 'data': 'test data' } #A dictionary of your post data
        post_body = urllib.urlencode(post_data) #Make it into a post request

        # response = yield client.fetch("http://localhost/collate", method='POST', body=post_body)

        # Test contents of response
        pass
