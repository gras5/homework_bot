import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
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
    """Отправляет сообщение в чат Telegram"""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logger.error(
            f'Произошла ошибка при отправке сообщения: {error}'
        )
    else:
        logger.info(
            f'Бот отправил сообщение: "{message}"'
        )


def get_api_answer(current_timestamp: int) -> dict:
    """Делает запрос к API с использованием временной метки"""
    timestamp = current_timestamp or int(time.time())
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': timestamp}

    try:
        response = requests.get(ENDPOINT, headers=headers, params=params)
    except Exception as error:
        raise Exception from error(
            f'Эндпоинт {ENDPOINT} недоступен. '
            f'Cообщение с ошибкой: {error}'
        )

    if response.status_code != 200:
        raise Exception(
            f'Эндпоинт {ENDPOINT} вернул неожиданный status_code. '
            f'Код ответа API: {response.status_code}'
        )

    return response.json()


def check_response(response: dict):
    """Проверяет полученный ответ от API на корректность"""
    homeworks = response['homeworks']
    homeworks_type = type(homeworks)

    if homeworks_type != list:
        raise TypeError(
            f'Неожиданный тип данных в списке домашек: {homeworks_type}'
        )

    return homeworks


def parse_status(homework: dict) -> str:
    """Извлекает из запроса имя и статус из записи домашней работы"""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    verdict = ''

    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError as e:
        raise KeyError(
            f'API вернул неизвестный статус домашней работы: {homework_status}'
        ) from e
    else:
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения для запуска бота"""
    env_vars = (
        ('PRACTICUM_TOKEN', PRACTICUM_TOKEN),
        ('TELEGRAM_TOKEN', TELEGRAM_TOKEN),
        ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID)
    )

    for env_var_name, value in env_vars:
        if not value:
            logger.critical(
                'Отсутствует обязательная переменная '
                f'окружения: {env_var_name}'
            )
            return False

    return True


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    cached_homeworks = None
    cached_message = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)

            homeworks = check_response(response)
            if cached_homeworks != homeworks:
                for homework in homeworks:
                    message_text = parse_status(homework)
                    cached_message = message_text
                    send_message(bot, cached_message)
            else:
                logger.debug(
                    'Полученный ответ не содержит '
                    'новых статусов домашних работ.'
                )

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'

            logger.error(message)
            if cached_message != message:
                send_message(bot, message)
                cached_message = message

            time.sleep(RETRY_TIME)
        else:
            cached_homeworks = homeworks


if __name__ == '__main__':
    main()
