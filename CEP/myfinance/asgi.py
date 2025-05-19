"""
ASGI config for myfinance project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myfinance.settings')
application = get_asgi_application()
