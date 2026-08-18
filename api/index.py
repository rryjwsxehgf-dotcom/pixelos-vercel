from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse
from api.core import generate_chat_reply

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        user_text = params.get('q', ['Привет'])[0]
        
        reply = generate_chat_reply(12345, user_text)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        res = {"status": "success", "prompt": user_text, "reply": reply}
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
