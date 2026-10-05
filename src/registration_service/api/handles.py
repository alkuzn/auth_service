from typing import Annotated
from random import random

from fastapi import Body, BackgroundTasks, Header, Request, Depends, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate

from aiologger.logger import Logger

from registration_service.api import app
from registration_service.schemes.schemes import RegisterData

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


async def is_email_used(email: str):
    # Запрос к сервису
    return email in ["test@mail.ru", "alex@gmail.com"]


async def send_code(email, code):
    await logger.info(f"Код {code} отправлен в брокеру")


@app.post(
    "/start-registration",
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(3, Duration.SECOND * 5))))],
)
async def start_registrations(
    request: Request,
    bgtasks: BackgroundTasks,
    user_agent: Annotated[str, Header()],
    data: Annotated[RegisterData, Body()],
):
    try:
        if await is_email_used(data.email):
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
    bgtasks.add_task(send_code, data.email, code)
    return {"success": True}