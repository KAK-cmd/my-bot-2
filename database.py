# database.py - работа с базой данных подписчиков
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name='bot_data.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        """Создает соединение с базой данных"""
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        """Инициализирует базу данных при первом запуске"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Таблица подписчиков
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscribers (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_notified TIMESTAMP
                )
            ''')
            
            # Таблица для логов рассылки (опционально)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mailing_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_type TEXT,
                    FOREIGN KEY (user_id) REFERENCES subscribers (user_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ База данных инициализирована")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")
    
    def add_subscriber(self, user_id: int, username: str = "", first_name: str = "", last_name: str = ""):
        """Добавляет подписчика (если уже есть - ничего не делает)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # INSERT OR IGNORE - если user_id уже есть, игнорируем
            cursor.execute('''
                INSERT OR IGNORE INTO subscribers 
                (user_id, username, first_name, last_name, subscribed_at) 
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Подписчик {user_id} добавлен/обновлен")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка добавления подписчика {user_id}: {e}")
            return False
    
    def remove_subscriber(self, user_id: int):
        """Удаляет подписчика"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM subscribers WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Подписчик {user_id} удален")
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Ошибка удаления подписчика {user_id}: {e}")
            return False
    
    def get_all_subscribers(self):
        """Получает список всех подписчиков"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT user_id FROM subscribers')
            subscribers = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            logger.info(f"✅ Получено {len(subscribers)} подписчиков")
            return subscribers
        except Exception as e:
            logger.error(f"❌ Ошибка получения подписчиков: {e}")
            return []
    
    def is_subscriber(self, user_id: int):
        """Проверяет, является ли пользователь подписчиком"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT 1 FROM subscribers WHERE user_id = ?', (user_id,))
            result = cursor.fetchone() is not None
            
            conn.close()
            return result
        except Exception as e:
            logger.error(f"❌ Ошибка проверки подписки {user_id}: {e}")
            return False
    
    def get_subscribers_count(self):
        """Возвращает количество подписчиков"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM subscribers')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        except Exception as e:
            logger.error(f"❌ Ошибка подсчета подписчиков: {e}")
            return 0
    
    def log_mailing(self, user_id: int, message_type: str):
        """Логирует отправку рассылки (для статистики)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO mailing_logs (user_id, message_type, sent_at)
                VALUES (?, ?, ?)
            ''', (user_id, message_type, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Ошибка логирования рассылки: {e}")
    
    def cleanup_old_logs(self, days: int = 30):
        """Удаляет старые логи (по желанию)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM mailing_logs 
                WHERE date(sent_at) < date('now', ?)
            ''', (f'-{days} days',))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Очищены логи старше {days} дней")
        except Exception as e:
            logger.error(f"❌ Ошибка очистки логов: {e}")

# Создаем глобальный экземпляр БД
db = Database()