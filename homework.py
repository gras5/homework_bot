import logging
import os
import sys
import time
import traceback
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from telegram.error import TelegramError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(funcName)s (%(lineno)d) %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot: telegram.Bot, message: str):
    """Отправляет сообщение в чат Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except TelegramError as error:
        t, m, tr = sys.exc_info()
        logger.error(
            f'Произошла ошибка при отправке сообщения: {message}\n'
            f'Текст сообщения: {error} \n'
            f'Отчет трассировки: {traceback.print_tb(tr)}'
        )
    else:
        logger.info(
            f'Бот отправил сообщение: {message}'
        )


def get_api_answer(current_timestamp: int) -> dict:
    """Делает запрос к API с использованием временной метки."""
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}

    try:
        response = requests.get(ENDPOINT, headers=headers, params=params)
    except ConnectionError as error:
        raise ConnectionError(
            f'Эндпоинт {ENDPOINT} недоступен. '
            f'Cообщение с ошибкой: {error}'
        ) from error

    if response.status_code != HTTPStatus.OK:
        raise Exception(
            f'Эндпоинт {ENDPOINT} вернул неожиданный status_code. '
            f'Код ответа API: {response.status_code}'
        )

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as error:
        raise requests.exceptions.JSONDecodeError(
            'Произошла ошибка при декодировании response из json в тип Python'
        ) from error


def check_response(response: dict):
    """Проверяет полученный ответ от API на корректность."""
    if not isinstance(response, dict):
        raise TypeError(
            'Полученный ответ API имеет тип отличный от dict. '
            f'Полученный тип: {type(response)}'
        )

    try:
        homeworks = response['homeworks']
    except KeyError as error:
        raise KeyError(
            f'Словарь response не содержит пары с ключом: {error}'
        ) from error

    if not isinstance(homeworks, list):
        raise TypeError(
            f'Неожиданный тип данных в списке домашек: {type(homeworks)}'
        )

    return homeworks


def parse_status(homework: dict) -> str:
    """Извлекает из запроса имя и статус из записи домашней работы."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError as error:
        raise KeyError(
            f'Объект homework не содержит ключа: {error}'
        ) from error

    if homework_status not in HOMEWORK_STATUSES:
        raise KeyError(
            f'API вернул неизвестный статус домашней работы: {homework_status}'
        )

    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения для запуска бота."""
    env_vars = (
        ('PRACTICUM_TOKEN', PRACTICUM_TOKEN),
        ('TELEGRAM_TOKEN', TELEGRAM_TOKEN),
        ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID)
    )

    tokens_exists = all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))
    env_none_vars = list(filter(lambda env_var: not env_var[1], env_vars))

    if not tokens_exists:
        logger.critical(
            'Отсутствует обязательная переменная '
            f'окружения: {env_none_vars}'
        )

    return tokens_exists


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit(
            'Работа Telegram бота прервана.'
        )

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    cached_error_message = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)

            homeworks = check_response(response)
            if homeworks:
                message_text = parse_status(homeworks[0])
                send_message(bot, message_text)
            else:
                logger.info(
                    'Полученный ответ не содержит '
                    'новых статусов домашних работ.'
                )

            current_timestamp = response['current_date']
        except Exception as error:
            error_message = f'Сбой в работе программы: {error}'

            logger.error(error_message)
            if cached_error_message != error_message:
                send_message(bot, error_message)
                cached_error_message = error_message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
