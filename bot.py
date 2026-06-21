from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from forecaster import get_coords, send_request
from utils import parse_json, display_all_data
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

TOKEN = os.environ.get('telegram_token')
YANDEX_URL = 'https://api.weather.yandex.ru/graphql/query'
YANDEX_ACCESS_KEY = os.environ.get('access_key')

bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer('Привет! Я погодный бот.')

@dp.message(Command('weather'))
async def send_weather(message: types.Message, command: CommandObject):
    city = command.args
    if city is None:
        city = 'Тюмень'
    coords = get_coords(city)
    if coords is None:
        await message.answer('Не удалось вычислить координаты. Проверьте название города.')
        return
    json = send_request(YANDEX_URL, YANDEX_ACCESS_KEY, coords)
    if json is None:
        await message.answer('Не удалось запросить погоду. Попробуйте позже.')
        return
    weather_data = parse_json(json)
    if weather_data is None:
        await message.answer(f'Ошибка парсинга погодных данных. Необработанные данные: {json}')
        return
    answer = display_all_data(weather_data, city)

    await message.answer(answer)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())