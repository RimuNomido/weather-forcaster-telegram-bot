from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from forecaster import get_coords, send_request
from utils import parse_json, display_all_data, display_all_history
from dotenv import load_dotenv
from db import save_query, get_queries, get_queries_count, clear_queries
import json
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
    data_dict = send_request(YANDEX_URL, YANDEX_ACCESS_KEY, coords)
    if data_dict is None:
        await message.answer('Не удалось запросить погоду. Попробуйте позже.')
        return
    weather_data = parse_json(data_dict)
    if weather_data is None:
        await message.answer(f'Ошибка парсинга погодных данных. Необработанные данные: {data_dict}')
        return
    answer = display_all_data(weather_data, city)

    save_query(message.from_user.id, city, data_dict)

    await message.answer(answer)

@dp.message(Command('history'))
async def history_command(message: types.Message, command: CommandObject):
    arg = command.args
    user_id = message.from_user.id
    if arg is None:
        queries = get_queries(user_id)
        count_of_queries = get_queries_count(user_id)
        if count_of_queries == 0:
            await message.answer('История запросов пуста.')
            return
        count_of_displayed_queries = len(queries)
        answers_data = []
        for city, json_data in queries:
            dict_data = json.loads(json_data)
            weather_data = parse_json(dict_data)
            answer = display_all_data(weather_data, city)
            answers_data.append(answer)
        await message.answer(display_all_history(answers_data, count_of_displayed_queries, count_of_queries))
    elif arg == 'clear':
        clear_queries(user_id)
        await message.answer('История запросов успешно очищена.')
        
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())