from datetime import UTC, datetime, timedelta

from aiologger import Logger
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.db.models import User

logger: Logger = Logger.with_default_handlers(name=__name__)


class CodeCarrier:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def save_code(self, email, code, sessionid):
        key = f"auth_service:{sessionid[:10]}"
        await self.redis.hset(
            key,
            mapping={
                "email": email,
                "code": code,
                "sessionid": sessionid,
            },
        )
        await self.redis.expireat(key, datetime.now(UTC) + timedelta(minutes=2))
        await logger.info(f"Код {code} отправлен в брокеру")

    async def verify_auth_code(self, sessionid, code) -> dict | None:
        key = f"auth_service:{sessionid[:10]}"
        resp = await self.redis.hgetall(key)
        if resp and resp["sessionid"] == sessionid and resp["code"] == code:
            await self.redis.delete(key)
            return resp
        return None


async def email_exists(session: AsyncSession, email: str):
    stmt = select(User.uuid).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar() is not None


async def save_code(app_state, email, code, sessionid):
    await app_state.code_carrier.save_code(email, code, sessionid)
    ##?????
