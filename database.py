# database.py - упрощенная версия для Render
import logging
import os

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Вместо SQLite используем память для простоты
        self.subscribers = set()
        self.load_from_file()
    
    def load_from_file(self):
        """Пытаемся загрузить из временного файла (если есть)"""
        try:
            # На Render используем /tmp папку которая сохраняется между деплоями
            temp_file = '/tmp/bot_subscribers.txt'
            if os.path.exists(temp_file):
                with open(temp_file, 'r') as f:
                    for line in f:
                        user_id = line.strip()
                        if user_id.isdigit():
                            self.subscribers.add(int(user_id))
                logger.info(f"✅ Загружено {len(self.subscribers)} подписчиков из файла")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки БД: {e}")
    
    def save_to_file(self):
        """Сохраняем в файл"""
        try:
            temp_file = '/tmp/bot_subscribers.txt'
            with open(temp_file, 'w') as f:
                for user_id in self.subscribers:
                    f.write(f"{user_id}\n")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения БД: {e}")
    
    def add_subscriber(self, user_id: int, username: str = "", first_name: str = "", last_name: str = ""):
        """Добавляет подписчика"""
        try:
            self.subscribers.add(user_id)
            self.save_to_file()
            logger.info(f"✅ Подписчик {user_id} добавлен")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка добавления подписчика: {e}")
            return False
    
    def remove_subscriber(self, user_id: int):
        """Удаляет подписчика"""
        try:
            if user_id in self.subscribers:
                self.subscribers.remove(user_id)
                self.save_to_file()
                logger.info(f"✅ Подписчик {user_id} удален")
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка удаления подписчика: {e}")
        return False
    
    def get_all_subscribers(self):
        """Получает список всех подписчиков"""
        return list(self.subscribers)
    
    def is_subscriber(self, user_id: int):
        """Проверяет, является ли пользователь подписчиком"""
        return user_id in self.subscribers
    
    def get_subscribers_count(self):
        """Возвращает количество подписчиков"""
        return len(self.subscribers)

# Создаем глобальный экземпляр БД
db = Database()