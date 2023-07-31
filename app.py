# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, abort
from flask_jsglue import JSGlue
from email_utils import send_email
from flask_sqlalchemy import SQLAlchemy
from celery_config import celery_app
from flask_migrate import Migrate


app = Flask(__name__)
celery_app.conf.update(app.config)
jsglue = JSGlue(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscribers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    birthday = db.Column(db.Date)

    def __repr__(self):
        return '<Subscriber %r>' % self.email


class SentEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    opened = db.Column(db.Boolean, default=False)


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
        try:
            # если 'delay' можно привести к числу
            delay = int(data.get('delay'))
        except ValueError:
        # если 'delay' нельзя привести к числу
            delay = 0

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

            sent_email = SentEmail(email=subscriber.email, subject=subject)
            db.session.add(sent_email)
            db.session.commit()

            # Создаем содержимое письма и добавляем в него уникальное изображение для отслеживания
            tracking_image_url = url_for('track_open', email_id=sent_email.id, _external=True)
            # Добавляем ID письма в переменные шаблона
            template_vars["email_id"] = sent_email.id

            # Передаем название шаблона, данные для шаблона и email подписчика в функцию send_email
            # apply_async рассылка с задержкой
            send_email.apply_async(args=[template, template_vars, subscriber.email], countdown=delay)

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
        try:
            # если 'delay' можно привести к числу
            delay = int(data.get('delay'))
        except ValueError:
            # если 'delay' нельзя привести к числу
            delay = 0



        # Получаем текущую дату
        today = datetime.today().date()

        # Извлекаем всех подписчиков из базы данных
        subscribers = fetch_all_subscribers_from_database()


        for subscriber in subscribers:
            # Проверяем, есть ли у подписчика дата рождения
            if subscriber.birthday:
                # Если день рождения подписчика сегодня
                if subscriber.birthday.day == today.day and subscriber.birthday.month == today.month:
                    # Создаем словарь с данными для шаблона
                    template_vars = {
                        "subject": subject,
                        "content": content,
                        "name": subscriber.first_name or '',  # Значение по умолчанию - пустая строка
                        "last_name": subscriber.last_name or ''  # Значение по умолчанию - пустая строка
                    }

                    sent_email = SentEmail(email=subscriber.email, subject=subject)
                    db.session.add(sent_email)
                    db.session.commit()

                    # Создаем содержимое письма и добавляем в него уникальное изображение для отслеживания
                    tracking_image_url = url_for('track_open', email_id=sent_email.id, _external=True)
                    # Добавляем ID письма в переменные шаблона
                    template_vars["email_id"] = sent_email.id

                    # Передаем название шаблона, данные для шаблона и email подписчика в функцию send_email
                    send_email.apply_async(args=[template, template_vars, subscriber.email], countdown=delay)
        return jsonify(success=True)
    else:
        return render_template("create-mailing.html")


@app.route('/track-open/<int:email_id>')  # Метод отслеживания открытия письма
def track_open(email_id):
    sent_email = SentEmail.query.get(email_id)
    if sent_email is None:
        abort(404)  # Вернуть ошибку 404, если письмо не найдено
    sent_email.opened = True
    db.session.commit()
    return send_file('transparent.gif', mimetype='image/gif')


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


@app.route('/sent-emails')
def sent_emails():
    sent_emails = SentEmail.query.order_by(SentEmail.timestamp.desc()).all()
    return render_template('sent_emails.html', sent_emails=sent_emails)



if __name__ == '__main__':
    app.run(debug=True) # TODO debug убрать
# TODO - добавить файл с контактами
# TODO - серый фон когда модальное окно второе всплывает
# TODO - обработка ошибок, если не заполнены поля
# TODO тесты
# TODO - RabbitMQ в документацию
# TODO - добавить requariments.txt