from aiologger import Logger

logger: Logger = Logger.with_default_handlers(name=__name__)


class CodeCarrier:
    @classmethod
    async def send_code(cls, email, code):
        await logger.info(f"Код {code} отправлен в брокеру")

    @classmethod
    async def verify_auth_code(cls, email, code):
        await logger.info(f"Код {code} отправлен в брокеру")
        return True
