# -*- coding: utf-8 -*-
import unittest
from app import app, db, Subscriber
from datetime import date


class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    #  проверяет создание подписчика в базе данных
    def test_subscriber_creation(self):
        subscriber = Subscriber(email="test@email.com", first_name="Test", last_name="User", birthday=date(1996, 1, 1))
        db.session.add(subscriber)
        db.session.commit()

        saved_subscriber = Subscriber.query.filter_by(email="test@email.com").first()
        self.assertEqual(saved_subscriber.first_name, "Test")
