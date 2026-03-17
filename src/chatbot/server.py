from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pisces

class ChatHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/chat':
            length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(length))
            result = pisces.send_message(body.get('message', ''))
            replies = result if isinstance(result, list) else [result]
            self._respond({'replies': replies})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _respond(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, *args): pass

if __name__ == '__main__':
    print('Pisces server running on http://localhost:8000')
    HTTPServer(('localhost', 8000), ChatHandler).serve_forever()   