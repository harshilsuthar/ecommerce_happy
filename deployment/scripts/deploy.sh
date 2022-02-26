
#!/usr/bin/env bash
PROJECT=ecommerce_happy
TARGET_ENV=venv

PROJECT_DIR=/home/projects/${PROJECT}
VIRTUAL_ENV=${PROJECT_DIR}/venv

if [ ! -d ${VIRTUAL_ENV} ]
then
  virtualenv ${VIRTUAL_ENV} --python=python3
fi

. ${VIRTUAL_ENV}/bin/activate
pip install -r ${PROJECT_DIR}/requirements.txt

echo "Make the logs dir..."
mkdir -p ${PROJECT_DIR}/logs

sudo chmod +x ${PROJECT_DIR}/deployment/scripts/gunicorn_start.sh

echo "Copy supervisor.conf..."
sudo cp ${PROJECT_DIR}/deployment/conf/ecommerce_happy_supervisor.conf /etc/supervisor/conf.d/

echo "Copy nginx.conf..."
sudo cp ${PROJECT_DIR}/deployment/conf/ecommerce_happy_nginx.conf /etc/nginx/sites-enabled/

echo "Restart nginx and supervisor..."
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ecommerce_happy_gunicorn
sudo supervisorctl restart ecommerce_happy_celery_worker
sudo supervisorctl status