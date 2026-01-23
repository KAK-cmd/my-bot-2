# keep_alive.py - предотвращает сон бота на Render
from aiohttp import web
import threading
import asyncio
import time

class KeepAliveServer:
    def __init__(self, port=8080):
        self.port = port
        self.app = web.Application()
        self.runner = None
        
        # Настраиваем маршруты
        self.app.router.add_get('/', self.handle_root)
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/ping', self.handle_ping)
        
        # Статистика
        self.start_time = time.time()
        self.request_count = 0
    
    async def handle_root(self, request):
        self.request_count += 1
        uptime = time.time() - self.start_time
        html = f"""
        <html>
            <head><title>Telegram Bot</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>🤖 Telegram Bot Активен</h1>
                <p><strong>Статус:</strong> ✅ Работает</p>
                <p><strong>Аптайм:</strong> {uptime:.0f} секунд</p>
                <p><strong>Запросов:</strong> {self.request_count}</p>
                <p><strong>Порт:</strong> {self.port}</p>
                <p><em>Бот предотвращает сон с помощью периодических запросов</em></p>
            </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def handle_health(self, request):
        return web.json_response({
            'status': 'healthy',
            'bot': 'running',
            'timestamp': time.time()
        })
    
    async def handle_ping(self, request):
        return web.Response(text='pong')
    
    async def start(self):
        """Запускаем сервер"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, '0.0.0.0', self.port)
        await site.start()
        print(f"✅ Keep-alive сервер запущен на порту {self.port}")
        print(f"🌐 Откройте: http://localhost:{self.port}")
    
    async def stop(self):
        """Останавливаем сервер"""
        if self.runner:
            await self.runner.cleanup()

# Глобальный экземпляр
keep_alive = KeepAliveServer()