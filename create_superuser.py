import os
from django.contrib.auth.models import User

username = 'root'
password = os.environ.get('ROOT_PASSWORD', 'rootword')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, '', password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")
