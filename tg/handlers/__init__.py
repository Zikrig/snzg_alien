from aiogram import Dispatcher

from tg.handlers import callbacks, promo_verify, start


def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(promo_verify.router)
    dp.include_router(start.router)
    dp.include_router(callbacks.router)
