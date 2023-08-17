[Read in Russian (Читать на русском)](README_RU.md)

# Email Mailing Service

## Send newsletters using HTML layouts and a list of subscribers.

- HTML layouts are located in templates/layouts.
- The list of subscribers is stored in the DB.
- The form for creating a mailing list is filled in a modal window; there, you can also set a waiting time for deferred mailing.
- Depending on the template, different variables are used in the mailing layout.
- Email open tracking with the integration of an invisible image.
- Separate pages for adding/removing subscribers to/from the DB and tracking mailings.
- HTML макеты расположены в templates/layouts


## Installation

Follow the steps below to install and run the project on your machine:



1. Clone the repository: $ git clone https://github.com/Stanis4live/mailing_service.git
2. Navigate to the project directory: $ cd mailing_service
3. Create and activate a virtual environment.
4. Install dependencies: $ pip install -r requirements.txt
5. Install the Redis server, which is used for caching, message brokers, session storage, and other tasks: $ sudo apt install redis-server
6. Install the RabbitMQ message broker:
$ sudo apt-get update -y
$ sudo apt-get install -y rabbitmq-server
7. Start the RabbitMQ message broker:
$ sudo systemctl enable rabbitmq-server
$ sudo systemctl start rabbitmq-server
8. To ensure the correct operation of the service, enter your @mail address and password into the corresponding fields of the access.py file.
9. Start Celery: $ celery -A celery_config.celery_app worker —loglevel=info
10. Create a database (you need to be in the project directory):
$ flask db init
$ flask db migrate -m "initial migration"
$ flask db upgrade
11. Start the server: $ python app.py

