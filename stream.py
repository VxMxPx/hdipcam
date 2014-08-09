"""
Cam stream.
"""

import http.client

class Stream(object):
    """
    Access cam stream.
    """
    def __init__(self, url, method):
        self.connection = http.client.HTTPConnection(url, timeout=10)
        self._method = method

    def getimagebytes(self):
        """
        Grab image bytes from url.
        """
        self.connection.request("GET", self._method)
        response = self.connection.getresponse()
        if response.status != 200:
            raise Exception("Cannot conenct, response: %s" % response.status)
        else:
            return response.read()
