#!/usr/bin/env bash

echo "Celery start"

PROJECTDIR=/home/projects/ecommerce_happy/
VIRTUAL_ENV=/home/projects/ecommerce_happy/venv # Virtual env directory
DJANGO_SETTINGS_MODULE=ecommerce.settings.production # which settings file should Django use

cd $PROJECTDIR/src
. ${VIRTUAL_ENV}/bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$PROJECTDIR:$
export C_FORCE_ROOT="true"

exec celery -A ecommerce worker --beat --scheduler django --loglevel=info
