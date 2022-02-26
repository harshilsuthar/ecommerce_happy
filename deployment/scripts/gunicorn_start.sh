#!/bin/bash
NAME="ecommerce_happy" # Name of the application
DJANGODIR=/home/projects/ecommerce_happy/ # Django project directory
SOCKFILE=/home/projects/ecommerce_happy/run/gunicorn.sock # we will communicate using this unix socket
VIRTUAL_ENV=/home/projects/ecommerce_happy/venv # Virtual env directory
NUM_WORKERS=3 # how many worker processes should Gunicorn spawn (2 * num cores)
DJANGO_SETTINGS_MODULE=ecommerce.settings.production # which settings file should Django use
DJANGO_WSGI_MODULE=ecommerce.wsgi # WSGI module name
LOG_LEVEL=error

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR/src
. ${VIRTUAL_ENV}/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

echo yes | python manage.py collectstatic --noinput
# python manage.py seed
# ./manage migrate

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ${VIRTUAL_ENV}/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  -b 0.0.0.0:8000 \
  --bind=unix:$SOCKFILE \
  --log-level=$LOG_LEVEL \
  --log-file=/home/projects/ecommerce_happy/logs/app.log
