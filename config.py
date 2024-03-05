import requests
import datetime
from config import tg_bot_token, open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.utils import executor
import matplotlib.pyplot as plt

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)

async def get_weather_info(city):
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        city_name = data["name"]
        temperature = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = sunset_timestamp - sunrise_timestamp

        return (f"     {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}     \n"
                f"Погода в городе: {city_name}\nТемпература: {temperature}C° {weather_description}\n"
                f"Влажность: {humidity}%\nДавление: {pressure} Па\nВетер: {wind_speed} м/с\n"
                f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\n"
                f"Продолжительность дня: {length_of_the_day}")

    except Exception as ex:
        print(ex)
        return None

async def get_temperature_graph(city):
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        temperatures = []
        dates = []

        for forecast in data['list']:
            timestamp = forecast['dt']
            date = datetime.datetime.fromtimestamp(timestamp)
            day = date.strftime('%d.%m')

            if day not in dates:
                dates.append(day)
                temperatures.append([])

            index = dates.index(day)
            temperature = forecast['main']['temp']
            temperatures[index].append(temperature)

        average_temperatures = [sum(temp) / len(temp) for temp in temperatures]

        plt.figure(figsize=(8, 5))
        plt.plot(dates, average_temperatures, marker='o')
        plt.title('Средняя температура за день')
        plt.xlabel('День')
        plt.ylabel('Температура, °C')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('temperature_graph.png')

        return open('temperature_graph.png', 'rb')

    except Exception as ex:
        print(ex)
        return None

async def send_weather_info(message: types.Message, city):
    weather_text = await get_weather_info(city)
    temperature_graph = await get_temperature_graph(city)

    if weather_text and temperature_graph:
        await bot.send_message(message.chat.id, weather_text)
        await bot.send_photo(message.chat.id, temperature_graph)

    else:
        await message.reply("Проверьте название города!")

@dp.message_handler(commands=["start", "help"])
async def start_command(message: types.Message):
    if message.text == '/start':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton('/help')
        keyboard.add(button)
        await message.reply("Привет! Напишите /help, чтобы получить инструкции, для использования бота.", reply_markup=keyboard)
    elif message.text == '/help':
        await message.reply("Укажите название города, и я отправлю вам прогноз погоды. Доступные команды:\n /start - начать,\n /help - помощь")

@dp.message_handler()
async def get_weather(message: types.Message):
    city = message.text
    await send_weather_info(message, city)

if __name__ == '__main__':
    executor.start_polling(dp)
