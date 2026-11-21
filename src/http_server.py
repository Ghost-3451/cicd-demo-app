import json
import math
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from src.calculator import add


def handle_request(target):
    url = urlsplit(target)
    if url.path == '/health':
        return 200, {'status': 'ok'}
    if url.path != '/add':
        return 404, {'error': 'Not found'}

    query = parse_qs(url.query, keep_blank_values=True)
    if set(query) != {'a', 'b'} or any(len(v) != 1 for v in query.values()):
        return 400, {'error': 'Provide one numeric a and one numeric b'}
    try:
        a = float(query['a'][0])
        b = float(query['b'][0])
        if not math.isfinite(a) or not math.isfinite(b):
            raise ValueError('Non-finite input')
        result = add(a, b)
        if not math.isfinite(result):
            raise ValueError('Non-finite result')
    except (ValueError, OverflowError):
        return 400, {'error': 'a and b must be finite numbers'}

    if result.is_integer():
        result = int(result)
    return 200, {'result': result}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, payload = handle_request(self.path)
        body = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    with ThreadingHTTPServer(('0.0.0.0', 8080), Handler) as server:
        server.serve_forever()


if __name__ == '__main__':
    main()
