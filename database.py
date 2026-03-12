import sqlite3
import time
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Таблица групп (где бот модерирует)
    cursor.execute('''CREATE TABLE IF NOT EXISTS groups (
        group_id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT,
        language TEXT DEFAULT 'ru'
    )''')
    
    # Таблица каналов для проверки
    cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
        group_id INTEGER,
        channel TEXT,
        PRIMARY KEY (group_id, channel)
    )''')
    
    # Таблица целевых групп для проверки
    cursor.execute('''CREATE TABLE IF NOT EXISTS target_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_group_id INTEGER,  -- ID группы, где бот модерирует
        target_group_id INTEGER,   -- ID целевой группы для проверки
        target_group_name TEXT,
        target_group_username TEXT,
        UNIQUE(source_group_id, target_group_id)
    )''')
    
    # Таблица VIP
    cursor.execute('''CREATE TABLE IF NOT EXISTS vip (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        group_id INTEGER,
        expires INTEGER,
        is_global INTEGER DEFAULT 0
    )''')
    
    # Проверяем наличие колонки language
    try:
        cursor.execute('SELECT language FROM groups LIMIT 1')
    except:
        cursor.execute('ALTER TABLE groups ADD COLUMN language TEXT DEFAULT "ru"')
    
    conn.commit()
    conn.close()
    logger.info("✅ База данных проверена")

# ========== ГРУППЫ ==========

def get_groups():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        return cursor.execute('SELECT group_id, name, username, language FROM groups').fetchall()
    except Exception as e:
        logger.error(f"Ошибка получения групп: {e}")
        return []
    finally:
        conn.close()

def add_group(group_id, name, username):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT OR IGNORE INTO groups (group_id, name, username) VALUES (?,?,?)',
            (group_id, name, username)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Ошибка добавления группы: {e}")
        return False
    finally:
        conn.close()

def set_group_language(group_id, lang):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE groups SET language=? WHERE group_id=?', (lang, group_id))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Ошибка установки языка: {e}")
        return False
    finally:
        conn.close()

def get_group_language(group_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        result = cursor.execute('SELECT language FROM groups WHERE group_id=?', (group_id,)).fetchone()
        return result[0] if result else 'ru'
    except Exception as e:
        logger.error(f"Ошибка получения языка: {e}")
        return 'ru'
    finally:
        conn.close()

# ========== КАНАЛЫ ==========

def add_channel(group_id, channel):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        # Проверяем существование
        existing = cursor.execute(
            'SELECT * FROM channels WHERE group_id=? AND channel=?', 
            (group_id, channel)
        ).fetchone()
        
        if existing:
            return False, f"❌ Канал {channel} уже существует в этой группе"
        
        # Проверяем лимит
        count = cursor.execute('SELECT COUNT(*) FROM channels WHERE group_id=?', 
                              (group_id,)).fetchone()[0]
        if count >= 3:
            return False, "❌ Максимум 3 канала на группу"
        
        cursor.execute('INSERT INTO channels VALUES (?,?)', (group_id, channel))
        conn.commit()
        return True, f"✅ Канал {channel} добавлен"
    except Exception as e:
        return False, f"❌ Ошибка: {e}"
    finally:
        conn.close()

def get_channels(group_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        return [r[0] for r in cursor.execute('SELECT channel FROM channels WHERE group_id=?', 
                                           (group_id,)).fetchall()]
    except Exception as e:
        logger.error(f"Ошибка получения каналов: {e}")
        return []
    finally:
        conn.close()

def del_channel(group_id, channel):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM channels WHERE group_id=? AND channel=?', 
                      (group_id, channel))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Ошибка удаления канала: {e}")
        return False
    finally:
        conn.close()

def del_all_channels(group_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM channels WHERE group_id=?', (group_id,))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Ошибка удаления каналов: {e}")
        return False
    finally:
        conn.close()

# ========== ЦЕЛЕВЫЕ ГРУППЫ ==========

def add_target_group(source_group_id, target_group_id, target_group_name, target_group_username=None):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        # Проверяем лимит
        count = cursor.execute(
            'SELECT COUNT(*) FROM target_groups WHERE source_group_id=?', 
            (source_group_id,)
        ).fetchone()[0]
        
        from config import MAX_TARGET_GROUPS
        if count >= MAX_TARGET_GROUPS:
            return False, f"❌ Максимум {MAX_TARGET_GROUPS} целевых групп"
        
        cursor.execute(
            'INSERT OR IGNORE INTO target_groups (source_group_id, target_group_id, target_group_name, target_group_username) VALUES (?,?,?,?)',
            (source_group_id, target_group_id, target_group_name, target_group_username)
        )
        conn.commit()
        return True, f"✅ Целевая группа {target_group_name} добавлена"
    except Exception as e:
        return False, f"❌ Ошибка: {e}"
    finally:
        conn.close()

def get_target_groups(source_group_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        return cursor.execute(
            'SELECT target_group_id, target_group_name, target_group_username FROM target_groups WHERE source_group_id=?',
            (source_group_id,)
        ).fetchall()
    except Exception as e:
        logger.error(f"Ошибка получения целевых групп: {e}")
        return []
    finally:
        conn.close()

def del_target_group(source_group_id, target_group_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'DELETE FROM target_groups WHERE source_group_id=? AND target_group_id=?',
            (source_group_id, target_group_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Ошибка удаления целевой группы: {e}")
        return False
    finally:
        conn.close()

def del_all_target_groups(source_group_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM target_groups WHERE source_group_id=?', (source_group_id,))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Ошибка удаления целевых групп: {e}")
        return False
    finally:
        conn.close()

# ========== VIP ==========

def add_vip(user_id, username, first_name, days, group_id, is_global=0):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    expires = int(time.time()) + days * 86400
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO vip (user_id, username, first_name, group_id, expires, is_global) 
            VALUES (?,?,?,?,?,?)
        ''', (user_id, username, first_name, group_id, expires, is_global))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Ошибка добавления VIP: {e}")
        return False
    finally:
        conn.close()

def get_vip():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    now = int(time.time())
    try:
        return cursor.execute('''
            SELECT user_id, username, first_name, group_id, expires, is_global 
            FROM vip WHERE expires>?
        ''', (now,)).fetchall()
    except Exception as e:
        logger.error(f"Ошибка получения VIP: {e}")
        return []
    finally:
        conn.close()

def is_vip(user_id, group_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    now = int(time.time())
    try:
        result = cursor.execute('''
            SELECT * FROM vip WHERE user_id=? AND expires>? AND (group_id=? OR is_global=1)
        ''', (user_id, now, group_id)).fetchone()
        return result is not None
    except Exception as e:
        logger.error(f"Ошибка проверки VIP: {e}")
        return False
    finally:
        conn.close()

def del_vip(user_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM vip WHERE user_id=?', (user_id,))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Ошибка удаления VIP: {e}")
        return False
    finally:
        conn.close()

def del_all_vip():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM vip')
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Ошибка удаления VIP: {e}")
        return False
    finally:
        conn.close()