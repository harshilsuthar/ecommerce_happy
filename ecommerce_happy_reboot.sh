#!/usr/bin/env bash

cd /home/projects/ecommerce_happy
source venv/bin/activate
git stash -u
git pull origin main
python3 update_ip.py
sh deployment/scripts/deploy.sh