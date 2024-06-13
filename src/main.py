from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI
from redis.asyncio import Redis, ConnectionPool
from starlette.middleware.cors import CORSMiddleware

from src import redis
from src.bot.telegram.app import set_webhook, moon_app
from src.bot.router import router as bot_router
from src.config import app_configs, settings


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    # Startup
    pool = ConnectionPool.from_url(str(settings.REDIS_URL), max_connections=settings.REDIS_CONNECTION_POOL_SIZE)
    redis.redis_client = Redis(connection_pool=pool)

    if not settings.ENVIRONMENT.is_deployed:
        await set_webhook()

    await moon_app.initialize()
    await moon_app.start()

    yield

    # Shutdown
    await redis.redis_client.close()
    await pool.disconnect()

    await moon_app.stop()
    await moon_app.shutdown()


app = FastAPI(**app_configs, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
    )


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(bot_router, tags=["bot"])
