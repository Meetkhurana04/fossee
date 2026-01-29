# backend/backend/wsgi.py
"""
WSGI config for backend project.

WSGI = Web Server Gateway Interface
This file is used when deploying Django to production servers
like Apache, Nginx, or cloud platforms (Heroku, AWS, etc.)

For development, we use 'python manage.py runserver' instead.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()