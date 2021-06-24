import logging
import os
import time
from logging import FileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


class ParseHomeworkException(Exception):
    pass


class SendMessageException(Exception):
    pass


try:
    env_var = os.environ
    PRAKTIKUM_TOKEN = env_var['PRAKTIKUM_TOKEN']
    TELEGRAM_TOKEN = env_var['TELEGRAM_TOKEN']
    CHAT_ID = env_var['TELEGRAM_CHAT_ID']
    URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    AUTH_TOKEN = f'OAuth {PRAKTIKUM_TOKEN}'
    SLEEP_TIME = 5
    REQUEST_SLEEP_TIME = SLEEP_TIME * 60
    HOMEWORK_STATUSES = {
        'reviewing': 'Работа взята в ревью.',
        'approved': 'Ревьюеру всё понравилось, работа зачтена!',
        'rejected': 'К сожалению, в работе нашлись ошибки.'
    }
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except EnvironmentError as e:
    logging.error(f'Environment is not properly set: {e}')
    raise

bot = telegram.Bot(TELEGRAM_TOKEN)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


def parse_homework_status(homework):
    try:
        logging.debug('Parsing homework')
        homework_name = homework.get('homework_name')
        status = homework.get('status')

        if not (homework_name and status):
            logging.error('Attribute is not found')
            raise ParseHomeworkException('Attribute is not found')

        if status in HOMEWORK_STATUSES:
            verdict = HOMEWORK_STATUSES.get(status)
        else:
            raise ParseHomeworkException('Homework status is not found')

        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except ParseHomeworkException as e:
        logging.error(f'Error while parsing homework: {e}')
        raise


def get_homeworks(current_timestamp):
    logging.debug('Getting homeworks')
    headers = {'Authorization': AUTH_TOKEN}
    params = {'from_date': current_timestamp}

    try:
        homework_statuses = requests.get(URL, params=params, headers=headers)
        return homework_statuses.json()
    except requests.RequestException as e:
        logging.error(f'Error while requesting: {e}')
        raise


def send_message(message):
    logging.info('Sending message')
    result = bot.send_message(CHAT_ID, message)

    if result != message:
        logging.error('Error while sending message')
        raise SendMessageException('Message sent with error')

    return result


def main():
    logging.debug('Starting an app')
    current_timestamp = int(time.time())

    while True:
        try:
            new_homeworks = get_homeworks(current_timestamp)
            homeworks = new_homeworks.get('homeworks')

            if homeworks:
                for hw in homeworks:
                    send_message(parse_homework_status(hw))

            current_timestamp = new_homeworks.get('current_date')
            time.sleep(REQUEST_SLEEP_TIME)
        except Exception as e:
            ERROR_MESSAGE = f'Bot is down with error: {e}'
            logging.error(ERROR_MESSAGE)
            send_message(ERROR_MESSAGE)
            time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = FileHandler(f'{BASE_DIR}/log.log')
    logger.addHandler(handler)
    main()
