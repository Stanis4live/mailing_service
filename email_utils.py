# -*- coding: utf-8 -*-
from flask import url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from access import EMAIL, PASSWORD
from celery_config import celery_app
from jinja2 import Environment


# @celery_app.task
# def send_email(template_name, template_vars, to_emails):
#     from app import app
#     with app.app_context():
#         try:
#             with open('templates/layouts/{}.html'.format(template_name), 'r', encoding='utf-8') as file:
#                 template = file.read()
#
#             # Создаем URL-адрес изображения для отслеживания и добавляем его в содержимое электронной почты
#             tracking_image_url = url_for('track_open', email_id=template_vars['email_id'], _external=True)
#             template += '<img src="{}">'.format(tracking_image_url)
#
#             # заменяем переменные в шаблоне на их значения
#             content = Environment().from_string(template).render(**template_vars)
#
#             # Объект сообщения
#             message = MIMEMultipart("alternative")
#             message["Subject"] = template_vars.get('subject', 'No subject')
#             message["From"] = EMAIL
#             message["To"] = ', '.join(to_emails)
#             message.attach(MIMEText(content, "html"))
#
#             # Отправляем письмо
#             with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#                 server.login(EMAIL, PASSWORD)
#                 server.sendmail(EMAIL, to_emails, message.as_string())
#         except Exception as e:
#             print(str(e))


# название шаблона, значения переменных в виде словаря и to_emails (список адресов получателей)
@celery_app.task
def send_email(template_name, template_vars, to_emails):
    from app import app
    with app.app_context():
        with open('templates/layouts/{}.html'.format(template_name), 'rb') as file:
            template = file.read().decode('utf-8')

        # Создаем URL-адрес изображения для отслеживания и добавляем его в содержимое электронной почты
        # генерируем URL для маршрута track_open,
        # _external=True говорит url_for сгенерировать абсолютный URL, включая схему (http или https) и имя хоста
        # добавляем в HTML-шаблон письма тег изображения
        tracking_image_url = url_for('track_open', email_id=template_vars['email_id'], _external=True)
        template += '<img src="{}">'.format(tracking_image_url)

        # заменяем переменные в шаблоне на их значения, переданные в функцию render_template_string из Flask
        content = Environment().from_string(template).render(**template_vars)

        # Объект сообщения
        message = MIMEMultipart("alternative")
        message["Subject"] = template_vars.get('subject', 'No subject')
        message["From"] = EMAIL
        message["To"] = ', '.join(to_emails)
        message.attach(MIMEText(content, "html", "utf-8"))


        # Отправляем письмо
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, to_emails, message.as_string())
            server.close()
        except Exception as e:
            print(str(e))


