from http.server import BaseHTTPRequestHandler
import json, requests, urllib.parse
from urllib.parse import parse_qs, urlparse

def get_erik_reply(prompt):
    system_prompt = "Ты — Эрик, саркастичный и умный ИИ-ассистент. Отвечай кратко, по делу, с легким юмором."
    
    encoded_prompt = urllib.parse.quote(prompt)
    encoded_system = urllib.parse.quote(system_prompt)
    url = f"https://text.pollinations.ai/{encoded_prompt}?system={encoded_system}&model=openai"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200 and res.text.strip():
            return res.text.strip()
    except Exception:
        pass
        
    return "Связь перегружена. Попробуй еще раз через минуту."

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        user_text = params.get('q', ['Привет'])[0]
        
        reply = get_erik_reply(user_text)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        res = {"status": "success", "prompt": user_text, "reply": reply}
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
