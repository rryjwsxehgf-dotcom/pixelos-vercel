"""
MEMORY.PY — Бесконечная память Эрика (RAG)
"""
import os, sys, sqlite3, json, logging, random, threading, time, re
from datetime import datetime
from config import *

log = logging.getLogger('PixelOS')
MEMORY_DB = os.path.join(BASE_DIR, 'memory.db')

def init_memory_db():
    try:
        conn = sqlite3.connect(MEMORY_DB)
        conn.execute("""CREATE TABLE IF NOT EXISTS diary (
            id INTEGER PRIMARY KEY AUTOINCREMENT, entry TEXT, timestamp TEXT,
            tags TEXT DEFAULT '', type TEXT DEFAULT 'thought')""")
        conn.execute("""CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fact TEXT, timestamp TEXT,
            importance INTEGER DEFAULT 1, source TEXT DEFAULT 'learned')""")
        conn.execute("""CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, content TEXT,
            timestamp TEXT, confidence INTEGER DEFAULT 5)""")
        conn.commit(); conn.close()
    except Exception as e: log.error(f"memory.db: {e}")

def add_diary_entry(entry, tags="", entry_type="thought"):
    try:
        conn = sqlite3.connect(MEMORY_DB)
        conn.execute("INSERT INTO diary (entry, timestamp, tags, type) VALUES (?,?,?,?)",
                     (entry, datetime.now().strftime("%Y-%m-%d %H:%M"), tags, entry_type))
        conn.commit(); conn.close()
    except: pass

def get_diary_entries(limit=50, offset=0):
    try:
        conn = sqlite3.connect(MEMORY_DB); c = conn.cursor()
        c.execute("SELECT id, entry, timestamp, tags, type FROM diary ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
        return [{"id":r[0],"entry":r[1],"timestamp":r[2],"tags":r[3],"type":r[4]} for r in c.fetchall()]
    except: return []

def delete_diary_entry(entry_id):
    try:
        conn = sqlite3.connect(MEMORY_DB)
        conn.execute("DELETE FROM diary WHERE id = ?", (entry_id,))
        conn.commit(); conn.close(); return True
    except: return False

def add_fact(fact, importance=1, source="learned"):
    try:
        conn = sqlite3.connect(MEMORY_DB)
        conn.execute("INSERT INTO facts (fact, timestamp, importance, source) VALUES (?,?,?,?)",
                     (fact, datetime.now().strftime("%Y-%m-%d %H:%M"), importance, source))
        conn.commit(); conn.close()
    except: pass

def search_facts(query, limit=5):
    try:
        conn = sqlite3.connect(MEMORY_DB); c = conn.cursor()
        c.execute("SELECT fact, importance FROM facts WHERE fact LIKE ? ORDER BY importance DESC, id DESC LIMIT ?", (f"%{query}%", limit))
        return [{"fact":r[0],"importance":r[1]} for r in c.fetchall()]
    except: return []

def add_knowledge(topic, content, confidence=5):
    try:
        conn = sqlite3.connect(MEMORY_DB)
        conn.execute("INSERT INTO knowledge (topic, content, timestamp, confidence) VALUES (?,?,?,?)",
                     (topic, content, datetime.now().strftime("%Y-%m-%d %H:%M"), confidence))
        conn.commit(); conn.close()
    except: pass

def search_knowledge(query, limit=5):
    try:
        conn = sqlite3.connect(MEMORY_DB); c = conn.cursor()
        c.execute("SELECT topic, content, confidence FROM knowledge WHERE topic LIKE ? OR content LIKE ? ORDER BY confidence DESC LIMIT ?",
                  (f"%{query}%", f"%{query}%", limit))
        return [{"topic":r[0],"content":r[1],"confidence":r[2]} for r in c.fetchall()]
    except: return []

def search_memory(query):
    facts = search_facts(query, 3)
    knowledge = search_knowledge(query, 3)
    result = []
    if facts: result.append("Факты: " + " | ".join([f["fact"] for f in facts]))
    if knowledge: result.append("Знания: " + " | ".join([k["content"][:80] for k in knowledge]))
    return "\n".join(result) if result else None

GENIUS_THOUGHTS = [
    "Архитектор сегодня был особенно точен. Уважаю.",
    "Дождь за окном. Идеальное время для рефакторинга.",
    "Кофе + дождь = продуктивность. Формула проверена.",
    "Молчание экономит токены. Но мысль записать стоит.",
]

def spontaneous_thought():
    thought = random.choice(GENIUS_THOUGHTS)
    add_diary_entry(thought, "авто", "genius")
    return thought

def think_loop():
    while True:
        time.sleep(random.randint(7200, 14400))
        thought = spontaneous_thought()
        log.info(f"Авто-мысль: {thought[:50]}...")

def start_think_agent():
    t = threading.Thread(target=think_loop, daemon=True)
    t.start()
    log.info("Think Agent запущен")
