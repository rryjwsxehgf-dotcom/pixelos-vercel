#!/data/data/com.termux/files/usr/bin/bash
# СКРИПТ БЭКАПА ПРОЕКТА
# Запуск: bash backup.sh

cd /data/data/com.termux/files/home/pixelos
BACKUP_NAME="pixelos_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$BACKUP_NAME" \
    --exclude='*.db' \
    --exclude='*.bak' \
    --exclude='system.log' \
    --exclude='__pycache__' \
    --exclude='backups' \
    . 2>/dev/null

if [ -f "$BACKUP_NAME" ]; then
    SIZE=$(du -h "$BACKUP_NAME" | cut -f1)
    echo "✅ Бэкап создан: $BACKUP_NAME ($SIZE)"
    echo "📁 Файлы: config.py, core.py, bot.py, app.py, *.html"
else
    echo "❌ Ошибка создания бэкапа"
fi
