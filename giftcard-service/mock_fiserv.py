from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'giftcardId':'gc-mock-123'}).encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 9090), Handler)
    print('Mock Fiserv listening on :9090')
    server.serve_forever()
