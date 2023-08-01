# -*- coding: utf-8 -*-
import os
import tempfile
import uuid
import pytest
from app import app, db, Subscriber, SentEmail
from email_utils import send_email
from mock import patch, Mock
import datetime
from datetime import date


class TestApp:

    # проверяет создание подписчика
    def test_subscriber_creation(self):
        unique_email = "test" + str(uuid.uuid4()) + "@example.com"
        subscriber = Subscriber(email=unique_email, first_name="John", last_name="Doe", birthday=date(1990, 5, 4))
        db.session.add(subscriber)
        db.session.commit()

        result = db.session.query(Subscriber).filter_by(email=unique_email).first()
        assert result is not None
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.birthday == date(1990, 5, 4)


# проверяет функционал удаления подписчика
def test_delete_subscriber():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db.create_all()
        unique_email = "test" + str(uuid.uuid4()) + "@example.com"
        new_subscriber = Subscriber(email=unique_email, first_name='John', last_name='Doe', birthday=datetime.date(1990, 5, 4))
        db.session.add(new_subscriber)
        db.session.commit()

        response = client.post('/delete-subscriber', data={'delete_email': unique_email})
        assert response.status_code == 200


# проверяет создание рассылки
@patch('app.send_email.apply_async')
def test_create_mailing(send_email_mock):
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db.create_all()
        unique_email = "test" + str(uuid.uuid4()) + "@example.com"
        new_subscriber = Subscriber(email=unique_email, first_name='John', last_name='Doe', birthday=datetime.date(1990, 5, 4))
        db.session.add(new_subscriber)
        db.session.commit()

        data = {
            "subject": "Test Subject",
            "content": "Test Content",
            "template": "Test Template",
            "delay": 5
        }
        response = client.post('/create-mailing/general', json=data)

        send_email_mock.assert_called()
        assert response.status_code == 200
        assert b'success' in response.data

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

