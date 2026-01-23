# database.py - простая БД в памяти для Render
import json
import os

class Database:
    def __init__(self):
        self.file_path = '/tmp/bot_data.json'
        self.subscribers = set()
        self.load()
    
    def load(self):
        """Загружаем данные из файла"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    self.subscribers = set(data.get('subscribers', []))
        except:
            self.subscribers = set()
    
    def save(self):
        """Сохраняем данные в файл"""
        try:
            data = {'subscribers': list(self.subscribers)}
            with open(self.file_path, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def add_subscriber(self, user_id, **kwargs):
        self.subscribers.add(user_id)
        self.save()
        return True
    
    def remove_subscriber(self, user_id):
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            self.save()
            return True
        return False
    
    def get_all_subscribers(self):
        return list(self.subscribers)
    
    def is_subscriber(self, user_id):
        return user_id in self.subscribers
    
    def get_subscribers_count(self):
        return len(self.subscribers)

db = Database()