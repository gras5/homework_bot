# Homework bot
### Содержание:
 + [Использованные технологии](#Tech)
 + [Описание](#Description)
 + [Подготовка перед запуском](#Preparation)
 + [Как запустить проект](#EasyStart)
 + [Об авторе](#About)

<br>
<a id="Tech"></a>

### Использованные технологии:

* Python
* python-telegram-bot
* requests


<br>
<a name="Description"></a>

### Описание:

Telegram-бот оповещающий об изменении статуса домашней работы в Яндекс.Практикум

<br>
<a name="Preparation"></a>

### Подготовка перед запуском:

Для нормальной работы Telegram-бота необходимо наличие двух токенов и id вашего аккаунта в Telegram:
1)  Токен API Практикум.Домашка (для получения этого токена вы должны быть студентом одного из курсов в Яндекс.Практикум)
    Получить токен можно по этой [ссылке](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a).
2)  Токен вашего Telegram-бота
    Как создать и получить токен можно посмотреть [здесь](https://core.telegram.org/bots).
3)  ID вашего аккаунта Telegram
    Можно воспользоваться одним из этих ботов: [@getmyid_bot](https://t.me/getmyid_bot) или [@userinfobot](https://telegram.me/userinfobot)

<br>
<a id="EasyStart"></a>

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке или в терминале Linux:

```
git clone https://github.com/gras5/homework_bot.git
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать файл .env в основной папке со следующим содержанием:

```
PRACTICUM_TOKEN=your_practicum_homework_token
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Запустить проект:

```
python3 homework.py
```

После запуска проекта написать своему боту для старта отслеживания статуса ваших домашних работ. 


<br>
<a name="About"></a>

### Об авторе
Github: https://github.com/gras5
