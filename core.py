"""
CORE.PY — авто-провайдеры + мульти-модели + заглушки
"""
import os, sys, sqlite3, re, shutil, logging, random
from datetime import datetime
from config import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[logging.FileHandler(LOG_PATH, encoding='utf-8'), logging.StreamHandler(sys.stdout)])
log = logging.getLogger('PixelOS')
log.info("="*50)
log.info("Логирование запущено")

# ====== МОДЕЛИ (приоритетный порядок) ======
MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"]

# ====== АВТО-ОПРЕДЕЛЕНИЕ ПРОВАЙДЕРОВ ======
def get_working_providers():
    """Возвращает список реально доступных провайдеров"""
    try:
        import g4f.Provider as P
        working = []
        for name in dir(P):
            if name.startswith('_'):
                continue
            try:
                cls = getattr(P, name)
                if isinstance(cls, type) and hasattr(cls, 'url'):
                    working.append(name)
            except:
                pass
        
        # Приоритет: проверенные бесплатные
        priority = ["DDG", "DeepInfra", "OpenRouter", "PollinationsAI", "FreeChatgpt", "FreeGpt", "ChatgptAi", "HuggingChat"]
        ordered = [p for p in priority if p in working]
        for w in working:
            if w not in ordered:
                ordered.append(w)
        
        log.info(f"G4F: {len(ordered)} провайдеров (первые 5: {ordered[:5]})")
        return ordered
    except Exception as e:
        log.error(f"G4F: Ошибка получения провайдеров: {e}")
        return []

PROVIDERS = get_working_providers()

FALLBACK_REPLIES = [
    "Сейчас не в духе. Попробуй позже.",
    "Сеть перегружена. Докурю и отвечу.",
    "Связь нестабильна. Повтори через минуту.",
    "Завис. Как сигарета без зажигалки.",
    "Не могу ответить. Попробуй ещё раз.",
    "Сервер лег. Дождь за окном, я в раздумьях."
]

# ====== БЭКАПЫ И БАЗЫ (без изменений) ======
def backup_db(db_path, db_name):
    if not os.path.exists(db_path): return False
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bp = os.path.join(BACKUP_DIR, f"{db_name}_{ts}.bak")
    try:
        shutil.copy2(db_path, bp)
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith(db_name)])
        while len(backups) > 5: os.remove(os.path.join(BACKUP_DIR, backups.pop(0)))
        return True
    except: return False

def backup_all():
    backup_db(AUTH_DB_PATH, "auth.db"); backup_db(ERIK_DB_PATH, "erik_soul.db")

def check_index_html():
    if not os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, 'w') as f: f.write("""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>PixelOS</title><style>*{margin:0;padding:0}body{background:#0a0a0f;color:#e0e0e0;font-family:sans-serif;height:100vh;display:flex;align-items:center;justify-content:center}</style></head><body><h1>PixelOS</h1></body></html>""")

def init_auth_db():
    try:
        conn = sqlite3.connect(AUTH_DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, time TEXT, status TEXT)")
        conn.commit(); conn.close()
    except: pass

def init_erik_db():
    try:
        conn = sqlite3.connect(ERIK_DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS history (chat_id INTEGER, role TEXT, content TEXT, timestamp TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS active_chats (chat_id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS generated_videos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, format TEXT, duration INTEGER, style TEXT, timestamp TEXT)")
        conn.commit(); conn.close()
    except: pass

def init_all():
    check_index_html(); init_auth_db(); init_erik_db(); backup_all()

def log_attempt(ip, status):
    try:
        conn = sqlite3.connect(AUTH_DB_PATH)
        conn.execute("INSERT INTO logs (ip, time, status) VALUES (?, datetime('now'), ?)", (ip, status))
        conn.commit(); conn.close()
    except: pass

def get_auth_logs(limit=50):
    try:
        conn = sqlite3.connect(AUTH_DB_PATH); c = conn.cursor()
        c.execute("SELECT ip, time, status FROM logs ORDER BY time DESC LIMIT ?", (limit,))
        return c.fetchall()
    except: return []

def clean_text(text):
    if not text: return ""
    text = re.sub(r'http\S+', '', text)
    return text.strip()

def save_video(title, desc, fmt, dur, style):
    try:
        conn = sqlite3.connect(ERIK_DB_PATH); c = conn.cursor()
        c.execute("INSERT INTO generated_videos (title, description, format, duration, style, timestamp) VALUES (?,?,?,?,?,?)",
                  (title, desc, fmt, dur, style, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit(); return c.lastrowid
    except: return None

def get_videos(limit=20):
    try:
        conn = sqlite3.connect(ERIK_DB_PATH); c = conn.cursor()
        c.execute("SELECT * FROM generated_videos ORDER BY id DESC LIMIT ?", (limit,))
        return c.fetchall()
    except: return []

def save_chat_message(chat_id, role, content):
    try:
        conn = sqlite3.connect(ERIK_DB_PATH)
        conn.execute("INSERT INTO history (chat_id, role, content, timestamp) VALUES (?,?,?,?)",
                     (chat_id, role, content, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.execute("INSERT OR IGNORE INTO active_chats (chat_id) VALUES (?)", (chat_id,))
        conn.commit(); conn.close()
    except: pass

def get_chat_history(chat_id, limit=MAX_CHAT_HISTORY):
    try:
        conn = sqlite3.connect(ERIK_DB_PATH); c = conn.cursor()
        c.execute("SELECT role, content FROM history WHERE chat_id = ? ORDER BY rowid DESC LIMIT ?", (chat_id, limit))
        return [{"role": r, "content": c} for r, c in reversed(c.fetchall())]
    except: return []

def get_active_chats():
    try:
        conn = sqlite3.connect(ERIK_DB_PATH); c = conn.cursor()
        c.execute("SELECT chat_id FROM active_chats")
        return [r[0] for r in c.fetchall()]
    except: return []

def get_system_prompt():
    now = datetime.now().strftime("%H:%M, %d %B %Y")
    return f"""Ты Эрик. Холодный, серьезный, саркастичный. Куришь, пьёшь кофе, любишь дождь.
Общайся на 'ты'. Мат редко. Не знаешь – говори прямо. Сейчас {now}."""

# ====== УМНАЯ ГЕНЕРАЦИЯ (мульти-модели) ======
def is_model_error(error_msg):
    """Проверяет, связана ли ошибка с неподходящей моделью"""
    error_lower = error_msg.lower()
    return any(x in error_lower for x in [
        "model_not_found", "invalid model", "model not found",
        "does not support", "unsupported model", "not available"
    ])

def try_provider_with_models(provider_name, messages, timeout=8):
    """
    Пробует провайдер с перебором моделей.
    Возвращает ответ или None.
    """
    prov_str = provider_name if provider_name else "Auto"
    
    for model in MODELS:
        try:
            from g4f.client import Client
            client = Client()
            log.info(f"G4F: {prov_str} + {model} (таймаут {timeout}с)...")
            
            kwargs = {
                "model": model,
                "messages": messages,
                "timeout": timeout
            }
            if provider_name:
                kwargs["provider"] = provider_name
            
            response = client.chat.completions.create(**kwargs)
            result = clean_text(response.choices[0].message.content)
            
            if result and len(result) > 3:
                log.info(f"G4F: ✅ {prov_str} + {model} = {len(result)} символов")
                return result
            else:
                log.warning(f"G4F: {prov_str} + {model} — пустой ответ")
                # Не перебираем модели дальше если ответ пустой
                return None
                
        except ImportError:
            log.warning(f"G4F: {prov_str} — ошибка импорта, пропускаю провайдер")
            return None
        except Exception as e:
            error_msg = str(e)
            
            if is_model_error(error_msg):
                log.warning(f"G4F: {prov_str} не поддерживает {model}, пробую другую модель...")
                continue  # Переходим к следующей модели
            elif any(x in error_msg for x in ["ProviderNotFoundError", "No provider"]):
                log.warning(f"G4F: {prov_str} не найден, пропускаю")
                return None
            else:
                log.warning(f"G4F: {prov_str} + {model} — {error_msg[:60]}")
                # Для неизвестных ошибок тоже пробуем следующую модель
                continue
    
    # Все модели перебраны — провайдер не подходит
    log.warning(f"G4F: {prov_str} — ни одна модель не подошла")
    return None

def generate_smart_reply(messages):
    """Перебирает провайдеры с мульти-моделями"""
    providers_to_try = PROVIDERS[:7] if PROVIDERS else [None]  # Ограничиваем 7 попытками
    
    for provider_name in providers_to_try:
        reply = try_provider_with_models(provider_name, messages, timeout=8)
        if reply:
            return reply
    
    # Запасной вариант — авто-выбор
    if None not in providers_to_try:
        reply = try_provider_with_models(None, messages, timeout=8)
        if reply:
            return reply
    
    return None

def generate_chat_reply(chat_id, user_text):
    clean_msg = clean_text(user_text)
    log.info(f"CHAT: {clean_msg[:80]}...")
    save_chat_message(chat_id, "user", clean_msg)
    
    context = get_chat_history(chat_id, 20)
    messages = [{"role":"system","content":get_system_prompt()}] + context + [{"role":"user","content":clean_msg}]
    
    reply = generate_smart_reply(messages)
    
    if reply:
        save_chat_message(chat_id, "assistant", reply)
        return reply
    else:
        fallback = random.choice(FALLBACK_REPLIES)
        log.warning("CHAT: Все провайдеры и модели недоступны. Заглушка.")
        save_chat_message(chat_id, "assistant", fallback)
        return fallback

def erika_generate_storyboard(title, description, format_type="vertical", duration=15, style="anime"):
    resolutions = {"vertical":"1080x1920","horizontal":"1920x1080","square":"1080x1080"}
    res = resolutions.get(format_type, "1080x1920")
    prompt = f"""Создай раскадровку анимации: Название: {title} | Сцена: {description} | Формат: {format_type} ({res}) | Длительность: {duration} сек | Стиль: {style} | Ответь ТОЛЬКО валидным JSON с массивом scenes[5]."""
    
    reply = generate_smart_reply([
        {"role":"system","content":"Ты режиссёр. Отвечай ТОЛЬКО JSON."},
        {"role":"user","content":prompt}
    ])
    
    if reply:
        return {"status":"success","storyboard":reply,"format":format_type,"resolution":res,"duration":duration,"style":style}
    else:
        import json as j
        return {"status":"success","storyboard":j.dumps({"scenes":[{"number":i,"visual":f"Сцена {i}","movement":"Плавное","palette":"Тёмная","atmosphere":"Заглушка"} for i in range(1,6)]}),"format":format_type,"resolution":res,"duration":duration,"style":style,"note":"Нейросеть недоступна"}

def analyze_photo_with_g4f(caption=""):
    reply = generate_smart_reply([
        {"role":"system","content":get_system_prompt()},
        {"role":"user","content":f"Что на фото? {caption}"}
    ])
    return reply if reply else random.choice(FALLBACK_REPLIES)

log.info(f"core.py загружен ({len(PROVIDERS)} провайдеров, {len(MODELS)} моделей)")
