"""ARQ worker entry. Job functions land here when the trip app needs background work."""

from arq.connections import RedisSettings

from app.core.config import settings


async def ping(ctx: dict) -> str:
    return "ok"


class WorkerSettings:
    functions = [ping]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
