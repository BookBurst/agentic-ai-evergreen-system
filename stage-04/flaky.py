from http.server import BaseHTTPRequestHandler, HTTPServer

calls = 0

class Flaky(BaseHTTPRequestHandler):
    def do_GET(self):
        global calls
        calls += 1
        if calls == 1:
            self.send_response(503)       # busy
        elif calls == 2:
            self.send_response(429)       # too fast
            self.send_header("Retry-After", "2")  # seconds
        else:
            self.send_response(200)
        self.end_headers()
        self.wfile.write(b"hello" if calls > 2 else b"busy")

    def log_message(self, *args):
        print("server: call", calls)

HTTPServer(("127.0.0.1", 8077), Flaky).serve_forever()
