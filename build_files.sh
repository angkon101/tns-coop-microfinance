#!/bin/bash
echo "=== Installing Python dependencies ==="
python -m pip install -r requirements.txt

echo "=== Collecting Static Files ==="
python manage.py collectstatic --noinput --clear

echo "=== Build Complete ==="
