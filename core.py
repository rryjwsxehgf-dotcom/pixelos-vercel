import os, sqlite3
from datetime import datetime

BASE_DIR = "/tmp" if os.getenv("VERCEL") else os.path.dirname(os.path.abspath(__file__))
ERIK_DB_PATH = os.path.join(BASE_DIR, "erik_soul.db")

MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

def init_db():
    try:
        with sqlite3.connect(ERIK_DB_PATH) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS history (chat_id INTEGER, role TEXT, content TEXT, timestamp TEXT)")
            conn.commit()
    except Exception:
        pass

def get_system_prompt():
    now = datetime.now().strftime("%H:%M, %d %B %Y")
    return f"Ты Эрик. Холодный, серьезный, саркастичный. Куришь, пьёшь кофе, любишь дождь. Общайся на 'ты'. Мат редко. Не знаешь – говори прямо. Сейчас {now}."

def generate_chat_reply(chat_id, user_text):
    init_db()
    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": user_text}
    ]
    
    for model in MODELS:
        try:
            from g4f.client import Client
            client = Client()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                timeout=5
            )
            content = response.choices[0].message.content
            if content and len(content.strip()) > 0:
                return content.strip()
        except Exception:
            continue

    return "Сейчас не в духе. Попробуй позже."
