# -*- coding: utf-8 -*-
from celery import Celery

celery_app = Celery('your_application', broker='pyamqp://guest@localhost//')


