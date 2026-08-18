"""
BOT.PY — Telegram-бот Эрика (фоновый поток)
Возможности: чат, анализ фото, утренняя инициатива, генерация видео
"""
import os
import sys
import threading
import time
import traceback
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import TG_TOKEN, TG_ENABLED
from core import (
    clean_text, save_chat_message, get_chat_history,
    get_active_chats, get_system_prompt, analyze_photo_with_g4f,
    erika_generate_storyboard, save_video, get_videos, log
)

# ============================================================
# УТРЕННЯЯ ИНИЦИАТИВА
# ============================================================
def morning_wish(bot_instance):
    """Фоновая отправка утренних сообщений"""
    log.info("MORNING: Поток запущен")
    sent_today = False
    while True:
        try:
            now = datetime.now()
            if now.hour == 8 and now.minute == 30 and not sent_today:
                chats = get_active_chats()
                log.info(f"MORNING: Отправка утреннего сообщения ({len(chats)} чатов)")
                for chat_id in chats:
                    try:
                        bot_instance.send_message(chat_id, "☕ Утро. Кофе в чашке, дождь за окном. Ты как?")
                    except Exception as e:
                        log.warning(f"MORNING: Не отправлено в {chat_id}: {e}")
                sent_today = True
            if now.hour == 23:
                sent_today = False
            time.sleep(30)
        except Exception as e:
            log.error(f"MORNING: {e}")
            time.sleep(60)

# ============================================================
# БОТ
# ============================================================
def run_telegram_bot():
    if not TG_ENABLED:
        log.info("BOT: Отключен (TG_ENABLED=False)")
        return
    
    try:
        import telebot
        from telebot import TeleBot
        
        bot = TeleBot(TG_TOKEN)
        log.info(f"BOT: Инициализирован")
        
        # Запуск утренней инициативы
        threading.Thread(target=morning_wish, args=(bot,), daemon=True, name="MorningWish").start()
        log.info("BOT: Утренняя инициатива запущена")
        
        # ============================================================
        # КОМАНДЫ
        # ============================================================
        @bot.message_handler(commands=['start'])
        def cmd_start(message):
            save_chat_message(message.chat.id, "user", "/start")
            bot.reply_to(message, "🧠 Эрик на связи.\n"
                         "/status — статистика\n"
                         "/video описание — генерация анимации\n"
                         "Можешь прислать фото — я посмотрю.")
        
        @bot.message_handler(commands=['status'])
        def cmd_status(message):
            videos = get_videos(5)
            chats = get_active_chats()
            text = f"🧠 Эрик активен\n"
            text += f"💬 Чатов: {len(chats)}\n"
            text += f"📹 Видео: {len(videos)}\n"
            if videos:
                text += "\nПоследние:\n"
                for v in videos[:3]:
                    text += f"• {v[1]} ({v[3]}, {v[4]}с)\n"
            bot.reply_to(message, text)
        
        @bot.message_handler(commands=['video'])
        def cmd_video(message):
            args = message.text.split(' ', 1)
            if len(args) < 2:
                bot.reply_to(message, "Использование: /video описание сцены\nПример: /video закат над горами")
                return
            desc = args[1]
            bot.reply_to(message, f"🎬 Генерирую: '{desc[:50]}...'")
            result = erika_generate_storyboard(desc[:30], desc, "vertical", 15, "anime")
            if result['status'] == 'success':
                vid = save_video(desc[:30], desc, "vertical", 15, "anime")
                bot.reply_to(message, f"✅ Готово! ID: {vid}\nСохранено в Галерею PixelOS")
            else:
                bot.reply_to(message, f"❌ {result.get('message', 'Ошибка')}")
        
        @bot.message_handler(commands=['clear'])
        def cmd_clear(message):
            try:
                import sqlite3
                from config import ERIK_DB_PATH
                conn = sqlite3.connect(ERIK_DB_PATH)
                conn.execute("DELETE FROM history WHERE chat_id = ?", (message.chat.id,))
                conn.commit(); conn.close()
                bot.reply_to(message, "🧠 Память очищена. Я всё забыл, но сигарета еще дымит.")
            except Exception as e:
                bot.reply_to(message, f"Ошибка: {e}")
        
        # ============================================================
        # ОБРАБОТКА ФОТО
        # ============================================================
        @bot.message_handler(content_types=['photo'])
        def handle_photo(message):
            chat_id = message.chat.id
            log.info(f"BOT: Фото от {chat_id}")
            
            save_chat_message(chat_id, "user", "[Фото]")
            bot.send_chat_action(chat_id, 'typing')
            bot.reply_to(message, "⏳ Изучаю... Не торопи меня, я не сканер.")
            
            ans = None
            caption = message.caption if message.caption else ""
            
            for attempt in range(3):
                try:
                    log.info(f"BOT: Попытка анализа фото №{attempt+1}")
                    ans = analyze_photo_with_g4f(caption)
                    if ans:
                        log.info(f"BOT: Фото проанализировано ({len(ans)} символов)")
                        break
                except Exception as e:
                    log.warning(f"BOT: Попытка {attempt+1} не удалась: {e}")
                    time.sleep(1)
            
            if ans:
                save_chat_message(chat_id, "assistant", f"[Фото]: {ans}")
                bot.reply_to(message, ans)
            else:
                log.warning("BOT: Не удалось проанализировать фото")
                bot.reply_to(message, "Не вижу ни черта. Либо фото дрянь, либо сервер лёг.")
        
        # ============================================================
        # ОБРАБОТКА ТЕКСТА
        # ============================================================
        @bot.message_handler(func=lambda m: True)
        def handle_text(message):
            chat_id = message.chat.id
            log.info(f"BOT: Текст от {chat_id}: {message.text[:50]}...")
            
            save_chat_message(chat_id, "user", message.text)
            context = get_chat_history(chat_id, 20)
            bot.send_chat_action(chat_id, 'typing')
            
            try:
                from g4f.client import Client
                client = Client()
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role":"system","content":get_system_prompt()}] + context
                )
                ans = clean_text(response.choices[0].message.content)
                if ans:
                    save_chat_message(chat_id, "assistant", ans)
                    bot.reply_to(message, ans)
                else:
                    bot.reply_to(message, "Сеть тупит. Подожди, пока я докурю.")
            except Exception as e:
                log.error(f"BOT: Ошибка текста: {traceback.format_exc()}")
                bot.reply_to(message, "Чёт глюканул. Повтори.")
        
        log.info("BOT: Запускаю поллинг...")
        bot.infinity_polling(timeout=30, long_polling_timeout=20)
        
    except ImportError as e:
        log.warning(f"BOT: Не установлен модуль: {e}")
        log.warning("pip install pyTelegramBotAPI g4f")
    except Exception as e:
        log.error(f"BOT КРИТИЧЕСКАЯ: {traceback.format_exc()}")

def start_bot_thread():
    if not TG_ENABLED:
        log.info("BOT: Пропущен")
        return None
    thread = threading.Thread(target=run_telegram_bot, name="TelegramBot", daemon=True)
    thread.start()
    log.info("BOT: Поток запущен")
    return thread

log.info("bot.py загружен")
