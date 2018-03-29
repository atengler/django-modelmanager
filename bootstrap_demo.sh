#!/bin/bash

(which pyenv > /dev/null 2>&1 && pyenv versions | grep modelmanager > /dev/null 2>&1) || \
  { echo -e "You must have pyenv installed and modelmanager pyenv-virtualenv created:\n    https://github.com/pyenv/pyenv"; exit 1; }

pyenv activate modelmanager

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py compress --force

read -r -d '' USERS << EOM
from django.contrib.auth import get_user_model;
User = get_user_model();
User.objects.all().delete();
User.objects.create_superuser('admin', 'admin@example.com', 'Admin123');
demo1 = User.objects.create(username='demo1', email='demo1@example.com');
demo1.set_password('Demo123');
demo1.save();
EOM

echo $USERS | python manage.py shell

python manage.py runserver 0.0.0.0:8000
