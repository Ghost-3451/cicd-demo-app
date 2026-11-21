import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class ReservedPortHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({'reserved': True}).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


port = int(sys.argv[1]) if len(sys.argv) > 1 else 18081
with HTTPServer(('127.0.0.1', port), ReservedPortHandler) as server:
    print(f'READY: port {port} is reserved; press Ctrl+C to release it.',
          flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
