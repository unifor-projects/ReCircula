import socketio

import app.chat.events  # noqa: F401 — registers all socket.io event handlers
from app.chat.socketio_server import sio
from app.main import app

# Wrap the FastAPI app: socket.io intercepts /socket.io/*, everything else goes to FastAPI
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
