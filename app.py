"""
APP.PY — Flask-сервер PixelOS + Gallery API
"""
import os, sys, json, traceback
from functools import wraps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path: sys.path.insert(0, BASE_DIR)

from flask import Flask, request, Response, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash

from config import *
from core import *
from bot import start_bot_thread

app = Flask(__name__)
app.secret_key = SECRET_KEY

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            session['next_url'] = request.path
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

# ====== СТРАНИЦЫ ======
@app.route('/login')
def login_page():
    try:
        with open(LOGIN_HTML_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<h1>Ошибка</h1><p>{e}</p>", 500

@app.route('/logout')
def logout_page():
    return """
    <!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Выход</title><link rel="stylesheet" href="/static/css/style.css"><style>body{display:flex;align-items:center;justify-content:center;flex-direction:column;gap:24px;height:100vh}</style></head><body><h1 style="font-family:var(--font-display);letter-spacing:2px">🚪 ВЫХОД</h1><div style="display:flex;gap:12px"><a href="/" class="btn">ОТМЕНА</a><a href="/api/logout" class="btn btn--danger">ВЫЙТИ</a></div></body></html>
    """

@app.route('/')
@login_required
def home():
    try:
        if not os.path.exists(INDEX_PATH): check_index_html()
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<h1>Ошибка</h1><p>{e}</p>", 500

@app.route('/erik')
@login_required
def erik_page():
    try:
        with open(ERIK_HTML_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<h1>Ошибка</h1><p>{e}</p>", 500


# ====== DIARY API ======
@app.route('/diary')
@login_required
def diary_page():
    try:
        with open(os.path.join(BASE_DIR, 'diary.html'), 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "<h1>diary.html not found</h1>", 404

@app.route('/api/diary')
@login_required
def api_diary():
    from memory import get_diary_entries, get_all_facts
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    entries = get_diary_entries(limit, offset)
    return jsonify({"status":"success","entries":entries,"total":len(get_diary_entries(1000))})

@app.route('/api/diary/<int:entry_id>', methods=['DELETE'])
@login_required
def api_diary_delete(entry_id):
    from memory import delete_diary_entry
    if delete_diary_entry(entry_id):
        return jsonify({"status":"success"})
    return jsonify({"status":"error"}), 404



@app.route('/api/login', methods=['POST'])
def api_login():
    ip = request.remote_addr
    try:
        data = request.get_json()
        password = data.get('password','')
        if check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['authenticated'] = True
            session['ip'] = ip
            log_attempt(ip, "success")
            next_url = session.pop('next_url', '/')
            return jsonify({"status":"success","redirect":next_url})
        else:
            log_attempt(ip, "fail")
            return jsonify({"status":"error","message":"Access denied"}), 401
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

@app.route('/api/logout')
def api_logout():
    session.clear()
    return redirect(url_for('login_page'))

# ====== GALLERY API ======
@app.route('/api/gallery/list')
@login_required
def api_gallery_list():
    """Возвращает список изображений из localStorage (заглушка)"""
    return jsonify({"status":"ok","message":"Gallery data is client-side (localStorage)"})

@app.route('/api/gallery/delete/<int:image_id>', methods=['DELETE'])
@login_required
def api_gallery_delete(image_id):
    """
    Удаление изображения по индексу.
    Клиент сам управляет localStorage, сервер логирует удаление.
    """
    ip = request.remote_addr
    log.info(f"GALLERY: Запрос удаления #{image_id} от {ip}")
    
    # Проверка на валидность ID (защита от инъекций)
    if image_id < 0 or image_id > 1000:
        return jsonify({"status":"error","message":"Invalid image ID"}), 400
    
    # Логируем и подтверждаем
    log.info(f"GALLERY: Изображение #{image_id} удалено")
    return jsonify({"status":"success","message":f"Image #{image_id} deleted","deleted_id":image_id})

# ====== SYSTEM STATS ======
@app.route('/api/stats')
@login_required
def api_stats():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory()
        battery = None
        try:
            bat = psutil.sensors_battery()
            if bat:
                battery = {"percent": round(bat.percent,1), "charging": bat.power_plugged}
        except: pass
        return jsonify({
            "status":"ok","cpu":cpu,
            "ram_percent":ram.percent,"ram_used":round(ram.used/(1024**3),1),"ram_total":round(ram.total/(1024**3),1),
            "battery":battery
        })
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

# ====== ОСТАЛЬНЫЕ API ======
@app.route('/api/logs')
@login_required
def api_logs():
    log_attempt(request.remote_addr, "success")
    logs = get_auth_logs(50)
    return {"logs": [{"ip":l[0],"time":l[1],"status":l[2]} for l in logs]}

@app.route('/api/erika/generate', methods=['POST'])
@login_required
def api_erika_generate():
    try:
        data = request.get_json()
        result = erika_generate_storyboard(data.get('title',''),data.get('description',''),data.get('format','vertical'),int(data.get('duration',15)),data.get('style','anime'))
        if result['status']=='success': result['video_id']=save_video(data.get('title',''),data.get('description',''),data.get('format','vertical'),int(data.get('duration',15)),data.get('style','anime'))
        return jsonify(result)
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

@app.route('/api/erika/videos')
@login_required
def api_erika_videos():
    return jsonify({"videos":[{"id":v[0],"title":v[1],"description":v[2],"format":v[3],"duration":v[4],"style":v[5],"timestamp":v[6]} for v in get_videos(20)]})

@app.route('/api/erik/chat', methods=['POST'])
@login_required
def api_erik_chat():
    try:
        data = request.get_json()
        msg = data.get('message','').strip()
        if not msg: return jsonify({"status":"error","message":"Empty"}), 400
        return jsonify({"status":"success","reply":generate_chat_reply(hash(request.remote_addr)%100000,msg)})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

if __name__ == "__main__":
    print("\n" + "="*55)
    print("🧠 PIXEL OS + GALLERY DELETE API")
    print("="*55)
    init_all(); start_bot_thread()
    print(f"\n✅ http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"🖼️ Gallery API: DELETE /api/gallery/delete/<id>")
    print(f"🔑 Пароль: 5038474728282828\n")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
