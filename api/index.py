from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {"status": "success", "message": "PixelOS Vercel API работает!"}
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
