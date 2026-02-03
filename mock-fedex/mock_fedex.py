from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/fulfill':
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.end_headers()
            resp = {
                'status': 'ACK',
                'trackingId': 'FDX-MOCK-{}'.format(12345)
            }
            self.wfile.write(json.dumps(resp).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 9091), Handler)
    print('Mock FedEx listening on :9091')
    server.serve_forever()
