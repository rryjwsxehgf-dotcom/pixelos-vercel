import os, json, subprocess

# 1. Создаем папку api
os.makedirs("api", exist_ok=True)

# 2. Создаем vercel.json
vercel_config = {
    "version": 2,
    "builds": [{"src": "api/index.py", "use": "@vercel/python"}],
    "routes": [{"src": "/(.*)", "dest": "api/index.py"}]
}
with open("vercel.json", "w", encoding="utf-8") as f:
    json.dump(vercel_config, f, indent=2)

# 3. Создаем api/index.py
api_code = '''from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {"status": "success", "message": "PixelOS Vercel API работает!"}
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
'''
with open("api/index.py", "w", encoding="utf-8") as f:
    f.write(api_code)

print("Все файлы успешно созданы! Пушим в GitHub...")

# 4. Выполняем git push
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Fix Vercel deployment"])
subprocess.run(["git", "push"])

print("ГОТОВО! Проверьте деплой на Vercel через 1-2 минуты.")
