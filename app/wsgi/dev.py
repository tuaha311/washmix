"""
WSGI config for wm_django project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys

# sys.path.insert(0, '/opt/python/current/app/app')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.dev")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
