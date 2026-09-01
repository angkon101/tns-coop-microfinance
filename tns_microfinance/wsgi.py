import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tns_microfinance.settings')

application = get_wsgi_application()

# Automatic table verification and self-healing for Serverless Vercel runtime
if os.environ.get('VERCEL'):
    try:
        from django.db import connection
        from django.core.management import call_command
        tables = connection.introspection.table_names()
        if 'accounts_customuser' not in tables:
            print("Running initial database migrations on Vercel...")
            call_command('migrate', interactive=False)
            try:
                import seed_data
            except Exception as se:
                print(f"Seed notice: {se}")
    except Exception as e:
        print(f"Auto-migration check notice: {e}")

# WSGI entrypoint for Vercel Serverless Function
app = application
