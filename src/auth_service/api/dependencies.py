from typing import Annotated

from aiologger import Logger
from fastapi import Body, Request

from auth_service.api.exceptions import BadCodeException, DatabaseConnectionException
from auth_service.db import SessionMaker

logger: Logger = Logger.with_default_handlers(name=__name__)


async def get_db(request: Request):
    sess = SessionMaker()
    try:
        yield sess
    except ConnectionRefusedError as ex:
        msg = f"{request.state.id}; Ошибка подключения к базе данных: {str(ex)}"
        await logger.error(msg)
        raise DatabaseConnectionException(msg)
    finally:
        await sess.close()


async def verify_code(
    code: Annotated[str, Body()],
    sessionid: Annotated[str, Body()],
    request: Request,
):
    result = await request.app.state.code_carrier.verify_auth_code(sessionid, code)
    if not result:
        raise BadCodeException()
    return result


def get_request_id(request: Request):
    return request.state.id
