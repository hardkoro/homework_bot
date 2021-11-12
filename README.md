# Homework Bot

## Description

Homework bot requests Yandex.Practicum Homework API to return status of homework

Bot: [https://t.me/hardkoro_test_bot](https://t.me/hardkoro_test_bot)

## Technology Stack

[![Python](https://img.shields.io/badge/-Python-464646??style=flat-square&logo=Python)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/-Telegram-464646??style=flat-square&logo=Telegram)](https://web.telegram.org/z/)
[![Heroku](https://img.shields.io/badge/-Heroku-464646??style=flat-square&logo=Heroku)](https://www.heroku.com/)
[![GitHub](https://img.shields.io/badge/-GitHub-464646??style=flat-square&logo=GitHub)](https://github.com/)

- Python
- Telegram
- Heroku
- GitHub

## Deployment

- Clone repo and change directory to the cloned repo:

  ```bash
  git clone https://github.com/hardkoro/homework_bot.git
  ```

  ```bash
  cd homework_bot
  ```

- Create & activate virtual environment:

  ```
  python3 -m venv venv
  ```

  ```
  . venv/bin/activate/
  ```
  
- Install dependencies:

  ```
  pip install -r requirements.txt
  ```
  
- Create & fill .env file:

  ```
  touch .env
  ```

  ```
  PRAKTIKUM_TOKEN=...   /* your Yandex.Practicum Homrwork API token */
  TELEGRAM_TOKEN=...    /* your Telegram bot token */
  TELEGRAM_CHAT_ID=...  /* yout Telegram chat id */
  ```
  
- Run homework.py:

  ```
  python3 homework.py
  ```

## Author 

[Evgeny Korobkov](https://github.com/hardkoro/)
