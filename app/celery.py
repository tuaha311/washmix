# from __future__ import absolute_import, unicode_literals
#
# import os
#
# from celery import Celery
#
# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings.dev')
#
# app = Celery('app')
# from django.conf import settings
#
# # Load task modules from all registered Django app configs.
# app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# # app.autodiscover_tasks()
#
#
# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))
