import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from src.http_server import Handler, handle_request


class TestHttpLogic(unittest.TestCase):
    def test_health(self):
        self.assertEqual(handle_request('/health'), (200, {'status': 'ok'}))

    def test_add(self):
        self.assertEqual(handle_request('/add?a=2&b=3'), (200, {'result': 5}))

    def test_decimals(self):
        self.assertEqual(handle_request('/add?a=1.5&b=-2'),
                         (200, {'result': -0.5}))

    def test_invalid_numbers(self):
        for target in ['/add?a=text&b=3', '/add?a=&b=3',
                       '/add?a=nan&b=3', '/add?a=inf&b=3',
                       '/add?a=1e308&b=1e308']:
            with self.subTest(target=target):
                self.assertEqual(handle_request(target)[0], 400)

    def test_missing_or_duplicate_parameters(self):
        for target in ['/add?a=2', '/add?a=2&b=3&b=4',
                       '/add?a=2&b=3&c=4']:
            with self.subTest(target=target):
                self.assertEqual(handle_request(target)[0], 400)

    def test_unknown_path(self):
        self.assertEqual(handle_request('/missing')[0], 404)


class TestHttpTransport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      daemon=True)
        cls.thread.start()
        cls.base_url = 'http://127.0.0.1:{}'.format(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def test_health_over_http(self):
        with urlopen(self.base_url + '/health', timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response), {'status': 'ok'})

    def test_add_over_http(self):
        with urlopen(self.base_url + '/add?a=2&b=3', timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response), {'result': 5})

    def test_invalid_number_over_http(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.base_url + '/add?a=abc&b=3', timeout=3)
        self.assertEqual(caught.exception.code, 400)
        caught.exception.close()


if __name__ == '__main__':
    unittest.main()
