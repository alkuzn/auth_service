import secrets
from datetime import UTC, datetime, timedelta
from random import random
from typing import Annotated

import jwt
from aiologger.logger import Logger
from fastapi import APIRouter, BackgroundTasks, Body, Depends, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.api.dependencies import get_db, get_request_id, verify_code
from auth_service.api.exceptions import (
    DatabaseConnectionException,
    EmailExistsException,
)
from auth_service.api.func import email_exists, save_code
from auth_service.db.models import User
from auth_service.schemes.schemes import RegisterData

logger: Logger = Logger.with_default_handlers(name=__name__)

router = APIRouter()


@router.post(
    "/start-registration",
    # dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(100, Duration.SECOND * 5))))],
)
async def start_registration(
    bgtasks: BackgroundTasks,
    data: Annotated[RegisterData, Body()],
    request_id: Annotated[str, Depends(get_request_id)],
    session: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
):
    try:
        if await email_exists(session, data.email):
            raise EmailExistsException()
    except (TimeoutError, ConnectionError) as ex:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис недосупен. Повторите попытку позже",
        )
    code = int(random() // 0.0001)
    sessionid = secrets.token_hex(32)
    bgtasks.add_task(save_code, request.app.state, data.email, code, sessionid)
    await logger.info(f"{request_id}; registration started;")
    return {"success": True, "sessionid": sessionid}


@router.post(
    "/confirm",
    # dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(100, Duration.SECOND * 5))))],
)
async def confirm(
    bgtasks: BackgroundTasks,
    request_id: Annotated[str, Depends(get_request_id)],
    cached_data: Annotated[dict, Depends(verify_code)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    user = User(email=cached_data["email"])
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except Exception as ex:
        await logger.error(
            f"{request_id}; confirm; Ошибка при выполнении запроса к бд: {ex}"
        )
    user_id = user.uuid
    if user_id:
        await logger.info(f"{request_id}; Пользователь {user_id} создан")
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED, content={"success": True}
        )
    else:
        await logger.info(f"{request_id}; Ошибка создания пользователя")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"success": False}
        )


@router.post(
    "/login",
    dependencies=[
        #    Depends(RateLimiter(limiter=Limiter(Rate(100, Duration.SECOND * 5))))
    ],
)
async def login(
    bgtasks: BackgroundTasks,
    request_id: Annotated[str, Depends(get_request_id)],
    data: Annotated[RegisterData, Body()],
    session: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
):
    if not await email_exists(session, data.email):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Данный email не зарегистрирован."},
        )
    code = int(random() // 0.0001)
    sessionid = secrets.token_hex(32)
    await logger.info(f"{request_id}; login started")
    bgtasks.add_task(save_code, request.app.state, data.email, code, sessionid)
    return {"success": True, "sessionid": sessionid}


@router.post(
    "/continue_login",
    # dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(100, Duration.SECOND * 5))))],
)
async def continue_login(
    bgtasks: BackgroundTasks,
    request_id: Annotated[str, Depends(get_request_id)],
    cached_data: Annotated[dict, Depends(verify_code)],
    session: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
):
    exp = datetime.now(UTC) + request.app.state.jwt_timedelta
    data = {"data": {"email": cached_data["email"]}, "exp": exp}
    token = jwt.encode(data, key=request.app.state.jwt_key, algorithm="HS256")
    await logger.info(f"{request_id}; Пользователь вошёл")
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED, content={"success": True, "token": token}
    )
