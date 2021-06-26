import logging
import os
import time
from json.decoder import JSONDecodeError
from logging import FileHandler

import requests
import telegram
from dotenv import load_dotenv
from requests.models import HTTPError
from urllib3.exceptions import ConnectTimeoutError

load_dotenv()


class ParseHomeworkException(Exception):
    pass


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
SLEEP_TIME = 5
REQUEST_SLEEP_TIME = SLEEP_TIME * 60
HOMEWORK_STATUSES = {
    'reviewing': 'Работа взята в ревью.',
    'approved': 'Ревьюеру всё понравилось, работа зачтена!',
    'rejected': 'К сожалению, в работе нашлись ошибки.'
}

ATTIRIBUTE_NOT_FOUND = 'Attribute {attr} not found'
STATUS_NOT_FOUND = 'Homework status {status} is not found'
UNKNOWN_STATUS = 'Unknown status: {status}'
HOMEWORK_RESULT = 'У вас проверили работу "{homework_name}"!\n\n{verdict}'
REQUEST_ERROR = (
    'Error while requesting url {url} with params {params}:\n\n{error}'
)
TELEGRAM_ERROR = (
    'Error while sending message via Telegram to chat id {chat_id}:\n\n{error}'
)
ERROR_MESSAGE = 'Bot is down with error: {error}'

try:
    env_var = os.environ
    PRAKTIKUM_TOKEN = env_var['PRAKTIKUM_TOKEN']
    AUTH_TOKEN = f'OAuth {PRAKTIKUM_TOKEN}'
    TELEGRAM_TOKEN = env_var['TELEGRAM_TOKEN']
    CHAT_ID = env_var['TELEGRAM_CHAT_ID']
except EnvironmentError as e:
    logging.error(f'Environment is not properly set: {e}')
    raise


bot = telegram.Bot(TELEGRAM_TOKEN)


def main():
    logging.debug('Starting an app')
    current_timestamp = int(time.time())

    while True:
        try:
            logging.debug('Getting homeworks')
            new_homeworks = get_homeworks(current_timestamp)
            logging.debug('JSON successfully decoded')
            homeworks = new_homeworks.get('homeworks')

            if homeworks:
                logging.info('Homeworks found')
                send_message(parse_homework_status(homeworks[0]))
            else:
                logging.info('Homeworks not found')

            current_timestamp = new_homeworks.get('current_date')
            logging.debug(f'Sleeping {REQUEST_SLEEP_TIME} before next try')
            time.sleep(REQUEST_SLEEP_TIME)
        except Exception as e:
            logging.error(ERROR_MESSAGE.format(error=e))
            send_message(ERROR_MESSAGE.format(error=e))
            time.sleep(SLEEP_TIME)


def get_homeworks(current_timestamp):
    headers = {'Authorization': AUTH_TOKEN}
    params = {'from_date': current_timestamp}

    try:
        logging.debug(f'Requesting: {URL}, {params}')
        homework_statuses = requests.get(URL, params=params, headers=headers)
    except HTTPError as e:
        raise HTTPError(REQUEST_ERROR.format(
            url=URL,
            params=params,
            error=e
        ))
    except ConnectionError as e:
        raise ConnectionError(REQUEST_ERROR.format(
            url=URL,
            params=params,
            error=e
        ))
    except ConnectTimeoutError as e:
        raise ConnectTimeoutError(REQUEST_ERROR.format(
            url=URL,
            params=params,
            error=e
        ))
    except Exception as e:
        raise Exception(REQUEST_ERROR.format(
            url=URL,
            params=params,
            error=e
        ))

    try:
        response = homework_statuses.json()
    except JSONDecodeError:
        raise JSONDecodeError

    if response.get('error'):
        raise Exception(REQUEST_ERROR.format(
            url=URL,
            params=params,
            error=response.get('error')['error']
        ))

    if response.get('code'):
        raise Exception(REQUEST_ERROR.format(
            url=URL,
            params=params,
            error=response.get('error')['code']
        ))

    return response


def parse_homework_status(homework):
    logging.debug('Parsing homework')
    homework_name = homework.get('homework_name')
    status = homework.get('status')

    if not homework_name:
        error = ATTIRIBUTE_NOT_FOUND.format(attr='homework_name')
        raise ParseHomeworkException(error)

    if not status:
        error = ATTIRIBUTE_NOT_FOUND.format(attr='status')
        raise ParseHomeworkException(error)

    if status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES.get(status)
    else:
        logging.warning(STATUS_NOT_FOUND.format(status=status))
        verdict = UNKNOWN_STATUS.format(status=status)

    return HOMEWORK_RESULT.format(
        homework_name=homework_name, verdict=verdict)


def send_message(message):
    logging.info('Sending message')

    try:
        return bot.send_message(CHAT_ID, message)
    except telegram.error.Unauthorized as e:
        raise telegram.error.Unauthorized(TELEGRAM_ERROR.format(
            chat_id=CHAT_ID,
            error=e
        ))
    except telegram.error.TelegramError as e:
        raise telegram.error.TelegramError(TELEGRAM_ERROR.format(
            chat_id=CHAT_ID,
            error=e
        ))
    except Exception as e:
        raise Exception(TELEGRAM_ERROR.format(
            chat_id=CHAT_ID,
            error=e
        ))


def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = FileHandler(f'{BASE_DIR}/log.log')
    logger.addHandler(handler)


if __name__ == '__main__':
    setup_logger()
    main()
