import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, setup_dialogs
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import Window
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from config import API_TOKEN, CAT_API_URL, CAT_API_KEY, NASA_API_URL, NASA_API_KEY

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

async def cat_button_click(callback: CallbackQuery, button: Button, manager: DialogManager):
    async with aiohttp.ClientSession() as session:
        headers = {'x-api-key': CAT_API_KEY}
        async with session.get(CAT_API_URL, headers=headers) as response:
            data = await response.json()
            cat_url = data[0]['url']
            await callback.message.answer_photo(cat_url, caption="Here is a cute cat!")

async def star_button_click(callback: CallbackQuery, button: Button, manager: DialogManager):
    async with aiohttp.ClientSession() as session:
        params = {'api_key': NASA_API_KEY}
        async with session.get(NASA_API_URL, params=params) as response:
            data = await response.json()
            star_url = data['url']
            explanation = data['explanation']
            await callback.message.answer_photo(star_url, caption=explanation)

class MainDialog(StatesGroup):
    START = State()

main_window = Window(
    Const("Choose an option:"),
    Row(
        Button(Const("Котики"), id="cats", on_click=cat_button_click),
        Button(Const("Звёзды"), id="stars", on_click=star_button_click)
    ),
    state=MainDialog.START
)

dialog = Dialog(main_window)

# Register start command
@router.message(CommandStart())
async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainDialog.START, mode=StartMode.RESET_STACK)

async def main():
    setup_dialogs(dp)
    dp.include_router(dialog)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())


