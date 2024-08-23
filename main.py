from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from Database import Database
import asyncio

dp = Dispatcher()
db = Database()
bot: Bot = None


async def dialog_started(id1: int, id2: int) -> None:
    db.set_chatting(id1, id2)
    db.set_chatting(id2, id1)
    await bot.send_message(text="Собеседник найден!\n\n/stop - остановить диалог\n/next - найти нового собеседника",
                           chat_id=id1)
    await bot.send_message(text="Собеседник найден!\n\n/stop - остановить диалог\n/next - найти нового собеседника",
                           chat_id=id2)


async def dialog_stopped(id1: int, id2: int) -> None:
    db.set_afk(id1)
    db.set_afk(id2)
    await bot.send_message(text="Диалог остановлен 🤧\n/start, чтобы начать поиск", chat_id=id1)
    await bot.send_message(text="Диалог остановлен 🤧\n/start, чтобы начать поиск", chat_id=id2)


async def start_finding(id_: int) -> None:
    db.set_finding(id_)
    finders = db.count_finders(id_)
    await bot.send_message(id_,
                           f"👍 Начинаю поиск собеседника\n\nСейчас в поиске: {finders} пользователей")
    companion = db.find_companion(id_)
    if companion != -1:
        await dialog_started(id_, companion)


@dp.message(CommandStart())
async def command_start(message: Message) -> None:
    if not db.is_in_data_base(message.from_user.id):
        db.add_user(message.from_user.id)
    if db.get_status(message.from_user.id) == 1:
        await bot.send_message(message.from_user.id, f"Вы уже в поиске диалога!")
        return
    await start_finding(message.from_user.id)


@dp.message(Command("stop"))
async def command_stop(message: Message) -> None:
    status = db.get_status(message.from_user.id)
    if status == 0:
        await message.answer("Вы не участвуете в диалоге!")
        return
    elif status == 1:
        db.set_afk(message.from_user.id)
        await message.answer("Вы больше не в поиске диалога!")
        return
    await dialog_stopped(message.from_user.id, db.get_companion(message.from_user.id))


@dp.message(Command("next"))
async def command_next(message: Message) -> None:
    status = db.get_status(message.from_user.id)
    if status != 2:
        await message.answer("Вы не участвуете в диалоге!")
        return
    await dialog_stopped(message.from_user.id, db.get_companion(message.from_user.id))
    await start_finding(message.from_user.id)


@dp.message()
async def echo(message: Message) -> None:
    comp = db.get_companion(message.from_user.id)
    if comp != 0:
        await message.send_copy(chat_id=comp)
    else:
        await message.answer("У вас нет собеседника! /start")


async def main() -> None:
    global bot
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


asyncio.run(main())
