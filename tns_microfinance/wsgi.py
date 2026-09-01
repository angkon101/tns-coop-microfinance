import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tns_microfinance.settings')

application = get_wsgi_application()

# WSGI entrypoint for Vercel Serverless Function
app = application
