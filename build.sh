#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install project dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Collect static files for Whitenoise
python manage.py collectstatic --noinput --clear

# Create superuser if environment variables are set and user does not exist
# This is a one-off setup. For subsequent deploys, if the superuser exists,
# this block will skip creation. For production, consider using a Render Job
# for one-off tasks like creating a superuser.
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Attempting to create superuser..."
    python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not User.objects.filter(username=username).exists():
    try:
        User.objects.create_superuser(username, email, password)
        print(f"Successfully created superuser '{username}'")
    except Exception as e:
        print(f"Error creating superuser: {e}")
else:
    print(f"Superuser '{username}' already exists. Skipping creation.")
EOF
    echo "Superuser creation command completed."
else
    echo "Skipping superuser creation: DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, or DJANGO_SUPERUSER_PASSWORD not all set."
fi
