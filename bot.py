from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from forecaster import get_coords, send_request
from utils import parse_json, display_weather_data, parse_query_to_story, display_all_history
from dotenv import load_dotenv
from db import save_query, get_queries, get_queries_count, clear_queries
from datetime import datetime
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
    answer = display_weather_data(weather_data, city)

    try:
        save_query(message.from_user.id, city, data_dict)
    except:
        await message.answer('При сохранении запроса в историю произошла ошибка. На данные прогноза это не повлияет.')

    await message.answer(answer)

@dp.message(Command('help'))
async def help_command(message: types.Message, command: CommandObject):
    answer = 'На данный момент доступны команды:\n' \
            '/weather [город] — бот покажет погоду по названию города / базовое значение — Тюмень;\n' \
            '/history — бот покажет последние 10 запросов;\n' \
            '/history clear — бот очистит историю запросов'
    await message.answer(answer)

@dp.message(Command('history'))
async def history_command(message: types.Message, command: CommandObject):
    arg = command.args
    user_id = message.from_user.id
    if arg is None:
        try:
            queries = get_queries(user_id)
            count_of_queries = get_queries_count(user_id)
            if count_of_queries == 0:
                await message.answer('История запросов пуста.')
                return
            count_of_displayed_queries = len(queries)
            answers_data = []
            for city, json_data, query_date in queries:
                dict_data = json.loads(json_data)
                weather_data = parse_json(dict_data)
                answer = parse_query_to_story(weather_data, city, query_date)
                answers_data.append(answer)
            await message.answer(display_all_history(answers_data, count_of_displayed_queries, count_of_queries))
        except Exception:
            await message.answer('При обращении к базе данных произошла непредвиденная ошибка. Попробуйте позже.')
    elif arg == 'clear':
        try:
            clear_queries(user_id)
            await message.answer('История запросов успешно очищена.')
        except:
            await message.answer('При очистке истории произошла ошибка. Попробуйте позже')
        
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())