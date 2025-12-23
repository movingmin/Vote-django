import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voteweb.settings")
django.setup()

from django.contrib.auth.models import User

username = 'root' # 관리자 계정 기본 아이디: root
password = os.environ.get('ROOT_PASSWORD', 'rootword') # 관리자 계정 기본 비밀번호: rootword

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, '', password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")
