# -*- coding: utf-8 -*-
from flask import url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from access import EMAIL, PASSWORD
from celery_config import celery_app
from jinja2 import Environment


# отправляет письмо
@celery_app.task
def send_email(template_name, template_vars, to_emails):
    from app import app
    with app.app_context():
        with open('templates/layouts/{}.html'.format(template_name), 'rb') as file:
            template = file.read().decode('utf-8')

        tracking_image_url = url_for('track_open', email_id=template_vars['email_id'], _external=True)
        template += '<img src="{}">'.format(tracking_image_url)

        content = Environment().from_string(template).render(**template_vars)

        message = MIMEMultipart("alternative")
        message["Subject"] = template_vars.get('subject', 'No subject')
        message["From"] = EMAIL
        message["To"] = ', '.join(to_emails)
        message.attach(MIMEText(content, "html", "utf-8"))

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, to_emails, message.as_string())
            server.close()
        except Exception as e:
            print(str(e))


