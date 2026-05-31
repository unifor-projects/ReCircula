import time
from collections import defaultdict

ONLINE_TTL = 300
RATE_LIMIT = 30
RATE_WINDOW = 60

_online: dict[int, float] = {}
_rate: dict[int, list[float]] = defaultdict(list)


async def set_online(user_id: int) -> None:
    _online[user_id] = time.monotonic() + ONLINE_TTL


async def refresh_online(user_id: int) -> None:
    if user_id in _online:
        _online[user_id] = time.monotonic() + ONLINE_TTL


async def set_offline(user_id: int) -> None:
    _online.pop(user_id, None)


async def is_online(user_id: int) -> bool:
    expires = _online.get(user_id)
    if expires is None:
        return False
    if time.monotonic() > expires:
        del _online[user_id]
        return False
    return True


async def check_rate_limit(user_id: int) -> bool:
    now = time.monotonic()
    window_start = now - RATE_WINDOW
    _rate[user_id] = [t for t in _rate[user_id] if t > window_start]
    if len(_rate[user_id]) >= RATE_LIMIT:
        return False
    _rate[user_id].append(now)
    return True
