# -*- coding: utf-8 -*-
from flask import render_template_string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content, To
from access import EMAIL, TOKEN
from celery_config import celery_app


# название шаблона, значения переменных в виде словаря и to_emails (список адресов получателей)
@celery_app.task
def send_email(template_name, template_vars, to_emails):
    with open('templates/layouts/{}.html'.format(template_name), 'rb') as file:
        template = file.read().decode('utf-8')
    # заменяем переменные в шаблоне на их значения, переданные в функцию render_template_string из Flask
    content = render_template_string(template, **template_vars)

    # создаёте объект Content, который содержит HTML-код (content) и должен быть интерпретирован как HTML ("text/html")
    content_obj = Content("text/html", content)

    # объект Mail - электронное письмо
    message = Mail(
        from_email=EMAIL,
        to_emails=To(to_emails),
    # пытаемся получить значение ключа 'subject' в словаре template_vars. Если ключ отсутствует, возвращается строка 'No subject'.
        subject=template_vars.get('subject', 'No subject'),
        html_content=content_obj)
    try:
    # создаем клиента SendGrid API, используя наш SendGrid API ключ.
        sg = SendGridAPIClient(TOKEN)
    # отправляем письмо, используя метод send клиента SendGrid API. Результат отправки сохраняется в переменной response.
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)


