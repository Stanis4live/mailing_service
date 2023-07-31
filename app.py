# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_jsglue import JSGlue
from email_utils import send_email
from flask_sqlalchemy import SQLAlchemy
from celery_config import celery_app


app = Flask(__name__)
celery_app.conf.update(app.config)
jsglue = JSGlue(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscribers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    birthday = db.Column(db.Date)

    def __repr__(self):
        return '<Subscriber %r>' % self.email


def fetch_all_subscribers_from_database():
    # Получаем все объекты модели Subscriber
    subscribers = Subscriber.query.all()
    return subscribers


@app.route("/", methods=["GET"])
def index():
    return render_template("create_mailing.html")


@app.route("/create-mailing/general", methods=["POST"])
def create_general_mailing():
    if request.method == "POST":
        # получение данных из AJAX-запроса
        data = request.get_json()
        subject = data.get("subject")
        content = data.get("content")
        template = data.get("template")

        # Извлекаем всех подписчиков из базы данных
        subscribers = fetch_all_subscribers_from_database()

        for subscriber in subscribers:
            # Создаем словарь с данными для шаблона
            template_vars = {
                "subject": subject,
                "content": content,
                "name": subscriber.first_name,
                "last_name": subscriber.last_name
            }
            # Передаем название шаблона, данные для шаблона и email подписчика в функцию send_email
            send_email.delay(template, template_vars, subscriber.email)
        return jsonify(success=True)
    else:
        return render_template("create-mailing.html")


@app.route("/create-mailing/birthday", methods=["POST"])
def create_birthday_mailing():
    if request.method == "POST":
        # получение данных из AJAX-запроса
        data = request.get_json()
        subject = data.get("subject")
        content = data.get("content")
        template = data.get("template")

        # Получаем текущую дату
        today = datetime.today().date()

        # Извлекаем всех подписчиков из базы данных
        subscribers = fetch_all_subscribers_from_database()

        for subscriber in subscribers:
            # Проверяем, есть ли у подписчика дата рождения
            if subscriber.birthday:
                # Если день рождения подписчика сегодня
                if subscriber.birthday.day == today.day and subscriber.birthday.month == today.month:
                    print (subscriber.email)
                    # Создаем словарь с данными для шаблона
                    template_vars = {
                        "subject": subject,
                        "content": content,
                        "name": subscriber.first_name or '',  # Значение по умолчанию - пустая строка
                        "last_name": subscriber.last_name or ''  # Значение по умолчанию - пустая строка
                    }
                    # Передаем название шаблона, данные для шаблона и email подписчика в функцию send_email
                    send_email.delay(template, template_vars, subscriber.email)
        return jsonify(success=True)
    else:
        return render_template("create-mailing.html")


@app.route('/database', methods=['GET', 'POST'])
def database():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthday = datetime.strptime(request.form['birthday'], '%Y-%m-%d')
        try:
            new_subscriber = Subscriber(email=email, first_name=first_name, last_name=last_name, birthday=birthday)
            db.session.add(new_subscriber)
            db.session.commit()
            redirect(url_for('index'))
        except Exception as exs:
            # все незавершенные изменения откатываются
            db.session.rollback()
            return exs

        return redirect(url_for('index')) # Перенаправление на главную страницу после успешного добавления подписчика

    else:
        return render_template('database.html')


@app.route('/delete-subscriber', methods=['POST'])
def delete_subscriber():
    email = request.form['delete_email']
    try:
        subscriber_to_delete = Subscriber.query.filter_by(email=email).first()
        if subscriber_to_delete:
            db.session.delete(subscriber_to_delete)
            db.session.commit()
            return "Subscriber deleted", 200
        else:
            return "Subscriber not found", 404
    except Exception as ex:
        db.session.rollback()
        return str(ex), 500



if __name__ == '__main__':
    app.run(debug=True) # TODO debug убрать
# TODO - добавить файл с контактами
# TODO - серый фон когда модальное окно второе всплывает
# TODO - обработка ошибок, если не заполнены поля
# TODO тесты
# TODO - RabbitMQ в документацию
# TODO - добавить requariments.txt