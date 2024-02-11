import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN_API
from menu import quiz_model


bot = Bot(TOKEN_API)
dp = Dispatcher()

async def main():

    dp.include_routers(quiz_model.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    