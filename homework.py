import logging
import os
import requests
import time

from dotenv import load_dotenv

from logging.handlers import RotatingFileHandler

from telegram import Bot

load_dotenv()

PRAKTIKUM_TOKEN = os.environ.get("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(funcName)s, %(name)s, %(message)s',
    filename='bot_log.log',
    filemode='a',
)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('bot_log.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    homework_statuses = requests.get(URL, params=params, headers=headers)
    return homework_statuses.json()


def send_message(message, bot_client):
    logging.info('Сообщение о статусе домашки отправлено в Telegram-чат')
    return bot_client.send_message(CHAT_ID, message)


def main():
    bot_client = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = '0000000000'
    logging.debug('Бот запущен')
    bot_client.send_message(CHAT_ID, 'Бот запущен')

    while True:
        try:
            new_hw = get_homework_statuses(current_timestamp)
            if new_hw.get('homeworks'):
                message = parse_homework_status(new_hw.get('homeworks')[0])
                send_message(message, bot_client)
            current_timestamp = new_hw.get('current_date', current_timestamp)
            time.sleep(1200)

        except Exception as e:
            err_message = f'Бот столкнулся с ошибкой: {e}'
            bot_client.send_message(CHAT_ID, err_message)
            logging.error(err_message)
            time.sleep(5)


if __name__ == '__main__':
    main()
