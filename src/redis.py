from datetime import timedelta

from redis.asyncio import Redis

from src.schemas import CustomModel

redis_client: Redis = None  # type: ignore


class RedisData(CustomModel):
    key: str
    value: bytes | str | int
    ttl: timedelta | int | None = None


async def set_redis_key(redis_data: RedisData, *, is_transaction: bool = False) -> None:
    async with redis_client.pipeline(transaction=is_transaction) as pipe:
        await pipe.set(redis_data.key, redis_data.value)
        if redis_data.ttl:
            await pipe.expire(redis_data.key, redis_data.ttl)

        await pipe.execute()


async def get_by_key(key: str) -> bytes | None:
    return await redis_client.get(key)


async def get_by_keys(keys: list[str]) -> list[bytes] | None:
    return await redis_client.mget(keys)


async def mset_keys(values: dict[str, str], ttl: int | timedelta | None = None) -> None:
    async with redis_client.pipeline() as pipe:
        await pipe.mset(values)
        if ttl:
            for key in values:
                await pipe.expire(key, ttl)

        await pipe.execute()


async def delete_by_key(key: str) -> None:
    return await redis_client.delete(key)


async def incr_by_key(key: str) -> None:
    return await redis_client.incrby(key)
