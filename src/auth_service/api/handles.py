from typing import Annotated
from random import random

from fastapi import Body, BackgroundTasks, Header, Request, Depends, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate

from aiologger.logger import Logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.api import app, CodeCarrier
from auth_service.schemes.schemes import RegisterData
from auth_service.db import User, SessionMaker

logger: Logger = Logger.with_default_handlers(name=__name__)


@app.exception_handler(RequestValidationError)
async def general_validation_handler(request: Request, ex: RequestValidationError):
    for err in ex.errors():
        match (err):
            case {"type": "value_error", "loc": ("body", field_name)}:
                msg = f"Невалидное поле {field_name}."
            case {"type": "missing", "loc": ("body", field_name)}:
                msg = f"Не указано поле {field_name}."
            case _:
                await logger.info(
                    f"{request.url.path}; unknown error; data={err} {request.headers['user-agent']}"
                )
                msg = "Неизвестная ошибка"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": msg}
    )


async def get_db():
    async with SessionMaker() as sess:
        yield sess


async def email_exists(session: AsyncSession, email: str):
    stmt = select(User.uuid).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar() is not None


@app.post(
    "/start-registration",
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(3, Duration.SECOND * 5))))],
)
async def start_registration(
    request: Request,
    bgtasks: BackgroundTasks,
    user_agent: Annotated[str, Header()],
    data: Annotated[RegisterData, Body()],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        if await email_exists(session, data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email уже используется."
            )
    except (TimeoutError, ConnectionError) as ex:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис недосупен. Повторите попытку позже",
        )

    await logger.info(f"{request.url.path}; registration started; {user_agent}")
    code = int(random() // 0.0001)
    bgtasks.add_task(CodeCarrier.send_code, data.email, code)
    return {"success": True}
