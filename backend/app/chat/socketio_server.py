import socketio

from app.config import settings

mgr = socketio.AsyncRedisManager(settings.REDIS_URL)

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_origins_list,
    client_manager=mgr,
    logger=False,
    engineio_logger=False,
)

sio_asgi_app = socketio.ASGIApp(sio, socketio_path="socket.io")
