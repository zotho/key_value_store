import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

MEMORY: Dict[str, Any] = dict()


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.protocol_version = "HTTP/1.1"
        self.close_connection = False

        parsed_url = urlparse(self.path)
        path = parsed_url.path
        keys = parse_qs(parsed_url.query).get("key")

        if path == "/keys":
            message = json.dumps(list(MEMORY.keys()))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        elif path == "/" and keys and all(key in MEMORY for key in keys):
            values = {key: MEMORY[key] for key in keys}
            message = json.dumps(values)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        else:
            message = "Error! Bad request"
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")

        self.send_header("Content-Length", len(message))
        self.end_headers()

        self.wfile.write(bytes(message, "utf8"))

    def do_POST(self):
        self.protocol_version = "HTTP/1.1"
        self.close_connection = False

        content_length = int(self.headers.get("Content-Length", 0))
        raw_post_data = self.rfile.read(content_length)

        try:
            data = json.loads(raw_post_data)
        except ValueError:
            data = None

        if data and isinstance(data, dict) and all(isinstance(key, str) for key in data):
            MEMORY.update(data)
            message = "OK"
            self.send_response(200)
        else:
            message = f"Error! Bad data: {data}"
            self.send_response(404)

        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", len(message))
        self.end_headers()

        self.wfile.write(bytes(message, "utf8"))

    def do_DELETE(self):
        self.protocol_version = "HTTP/1.1"
        self.close_connection = False

        content_length = int(self.headers.get("Content-Length", 0))
        raw_delete_data = self.rfile.read(content_length)

        try:
            data = json.loads(raw_delete_data)
        except ValueError:
            data = None

        keys = data and isinstance(data, dict) and data.get("key")
        if keys and all(key in MEMORY for key in keys):
            for key in keys:
                MEMORY.pop(key)
            message = "OK"
            self.send_response(200)
        else:
            message = f"Error! Bad data: {data}"
            self.send_response(404)

        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", len(message))
        self.end_headers()

        self.wfile.write(bytes(message, "utf8"))


def create_server(host="", port=0):
    return ThreadingHTTPServer((host, port), RequestHandler)


def run(host="", port=0):
    httpd = create_server(host, port)

    host, port = httpd.server_address
    print(f"Start serving on http://{host}:{port}")

    httpd.serve_forever()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        _, host, port = sys.argv
        run(host, int(port))
    else:
        run()
