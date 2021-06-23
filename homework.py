import logging
import os
import time
from logging import FileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(TELEGRAM_TOKEN)

logging.basicConfig(
    level=logging.DEBUG,
    filename='log.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


def parse_homework_status(homework):
    logging.debug('Parsing homework')
    homework_name = homework['homework_name']

    if homework['status'] != 'approved':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'

    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    logging.debug('Getting homeworks')
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    homework_statuses = requests.get(url, params=params, headers=headers)
    logging.debug('Getting response from api')
    return homework_statuses.json()


def send_message(message):
    logging.info('Sending message')
    return bot.send_message(CHAT_ID, message)


def main():
    logging.debug('Starting app')
    current_timestamp = int(time.time())

    while True:
        try:
            homeworks = get_homeworks(current_timestamp)

            for hw in homeworks['homeworks']:
                message = parse_homework_status(hw)
                send_message(message)

            time.sleep(5 * 60)
            current_timestamp += 5 * 60

        except Exception as e:
            ERROR_MESSAGE = f'Bot is down with error: {e}'
            logging.error(ERROR_MESSAGE)
            send_message(ERROR_MESSAGE)
            time.sleep(5)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = FileHandler('log.log')
    logger.addHandler(handler)
    main()
