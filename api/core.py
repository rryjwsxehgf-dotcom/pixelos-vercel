"""
CORE.PY — авто-провайдеры + мульти-модели + заглушки
"""
import os, sys, sqlite3, re, shutil, logging, random
from datetime import datetime

# Подтягиваем пути из config если есть, иначе дефолты
try:
    from config import *
except ImportError:
    LOG_PATH = "/tmp/pixelos.log"
    BACKUP_DIR = "/tmp/backups"
    AUTH_DB_PATH = "/tmp/auth.db"
    ERIK_DB_PATH = "/tmp/erik_soul.db"
    INDEX_PATH = "/tmp/index.html"
    MAX_CHAT_HISTORY = 20

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger('PixelOS')

MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"]

def get_working_providers():
    try:
        import g4f.Provider as P
        working = []
        for name in dir(P):
            if name.startswith('_'): continue
            try:
                cls = getattr(P, name)
                if isinstance(cls, type) and hasattr(cls, 'url'): working.append(name)
            except: pass
        priority = ["DDG", "DeepInfra", "OpenRouter", "PollinationsAI", "FreeChatgpt", "FreeGpt", "ChatgptAi", "HuggingChat"]
        ordered = [p for p in priority if p in working]
        for w in working:
            if w not in ordered: ordered.append(w)
        return ordered
    except Exception as e:
        return []

PROVIDERS = get_working_providers()

FALLBACK_REPLIES = [
    "Сейчас не в духе. Попробуй позже.",
    "Сеть перегружена. Докурю и отвечу.",
    "Связь нестабильна. Повтори через минуту.",
    "Завис. Как сигарета без зажигалки."
]

def clean_text(text):
    if not text: return ""
    return re.sub(r'http\S+', '', text).strip()

def try_provider_with_models(provider_name, messages, timeout=6):
    prov_str = provider_name if provider_name else "Auto"
    for model in MODELS:
        try:
            from g4f.client import Client
            client = Client()
            kwargs = {"model": model, "messages": messages, "timeout": timeout}
            if provider_name: kwargs["provider"] = provider_name
            response = client.chat.completions.create(**kwargs)
            result = clean_text(response.choices[0].message.content)
            if result and len(result) > 3: return result
        except Exception:
            continue
    return None

def generate_smart_reply(messages):
    providers_to_try = PROVIDERS[:5] if PROVIDERS else [None]
    for provider_name in providers_to_try:
        reply = try_provider_with_models(provider_name, messages, timeout=6)
        if reply: return reply
    return random.choice(FALLBACK_REPLIES)

