[Read in English (Читать на английском)](README.md)

# Сервис отправки email рассылок

## Отправка рассылок с использованием html макетов и списка подписчиков.

- HTML макеты расположены в templates/layouts
- Список подписчиков хранится в DB
- Форма для создания рассылки заполняется в модальном окне, там же можно задать время ожидание для отложенной рассылки -
- Использование переменных в макете рассылки, в зависимости от макета используются разные переменные
- Отслеживание открытий писем при помощи внедрения невидимого изображения
- Отдельные страницы для добавления/удаления подписчиков в/из DB и отслеживания рассылок

## Установка

Следуйте следующим шагам, чтобы установить и запустить проект на вашей машине:

1. Клонируем репозиторий $ git clone https://github.com/Stanis4live/mailing_service.git
2. Переходим в директорию проекта $ cd mailing_service
3. Создаём и активируем виртуальное окружение
4. Установка зависимостей $ pip install -r requirements.txt
5. Устанавливаем сервер Redis, которая используется для кэширования, брокеров сообщений, хранения сеансов и других вещей.
$ sudo apt install redis-server
6. Устанавливаем, брокер сообщений RabbitMQ
$ sudo apt-get update -y
$ sudo apt-get install -y rabbitmq-server
7. Запускаем брокер сообщений RabbitMQ
$ sudo systemctl enable rabbitmq-server
$ sudo systemctl start rabbitmq-server
8. Для корректной работы сервиса требуется внести @mail адрес и пароль в соответствующие поля файла access.py
9. Запускаем Celery $ celery -A celery_config.celery_app worker —loglevel=info
10. Создаём базу данных (необходимо находиться в директории проекта) 
$ flask db init
$ flask db migrate -m "initial migration"
$ flask db upgrade
11. Запускаем сервер $ python app.py
