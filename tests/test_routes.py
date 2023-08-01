# -*- coding: utf-8 -*-
import unittest
from app import app, db, Subscriber


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

# проверяет успешное выполнение запроса на главную страницу
    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

# проверяет успешное выполнение запроса на database
    def test_database_route_get(self):
        response = self.client.get('/database')
        self.assertEqual(response.status_code, 200)

# проверяет успешное выполнение запроса на sent-emails
    def test_sent_emails_route(self):
        response = self.client.get('/sent-emails')
        self.assertEqual(response.status_code, 200)
