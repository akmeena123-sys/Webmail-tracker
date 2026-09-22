import os
import socketserver
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8000


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, format, *args):
        # Keep console output clean and simple.
        return


if __name__ == '__main__':
    with ThreadingHTTPServer(('0.0.0.0', PORT), QuietHandler) as httpd:
        print(f'Webmail dashboard is running at http://localhost:{PORT}')
        print('Press Ctrl+C to stop the server.')
        httpd.serve_forever()
