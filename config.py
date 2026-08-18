"""
КОНФИГУРАЦИЯ PIXEL OS + ERIKA ENGINE
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')
ERIK_HTML_PATH = os.path.join(BASE_DIR, 'erik.html')
LOGIN_HTML_PATH = os.path.join(BASE_DIR, 'login.html')
AUTH_DB_PATH = os.path.join(BASE_DIR, 'auth.db')
ERIK_DB_PATH = os.path.join(BASE_DIR, 'erik_soul.db')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
LOG_PATH = os.path.join(BASE_DIR, 'system.log')

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "scrypt:32768:8:1$7P6zobhkdPmEe8fJ$e8514423e2588d30b8dd63f10869080a6c5299dc42ccc55c545971ec659edbdbd2e799845ea457259ac84a862530cebb1a1a6cf15a888d481f8ca674103d7d76"

FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = False
SECRET_KEY = "pixelos_super_secret_key_2026"

TG_TOKEN = '8788081502:AAE0UeKvacLaTebCsc97mk2ASUiYd1ZQUsg'
TG_ENABLED = True

AI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"]
AI_PRIORITY_PROVIDERS = ["DDG", "DeepInfra", "OpenRouter", "PollinationsAI", "FreeChatgpt", "FreeGpt", "ChatgptAi", "HuggingChat"]
AI_MAX_PROVIDERS = 3
AI_TIMEOUT = 5
AI_MIN_REPLY_LENGTH = 3

FALLBACK_REPLIES = [
    "Сейчас не в духе. Попробуй позже.",
    "Сеть перегружена. Докурю и отвечу.",
    "Связь нестабильна. Повтори через минуту.",
    "Завис. Как сигарета без зажигалки.",
    "Не могу ответить. Попробуй ещё раз.",
    "Сервер лег. Дождь за окном, я в раздумьях."
]

MAX_GALLERY_ITEMS = 50
MAX_LOG_ENTRIES = 100
MAX_CHAT_HISTORY = 30
MAX_BACKUPS = 5
ERIKA_MAX_SCENES = 5
ERIKA_DEFAULT_DURATION = 15
ERIKA_DEFAULT_STYLE = "anime"

print(f"[CONFIG] Загружен: {BASE_DIR}")

# === ОХЛАЖДЕНИЕ ===
AI_TIMEOUT = 4
AI_MAX_PROVIDERS = 2
MAX_CHAT_HISTORY = 10
