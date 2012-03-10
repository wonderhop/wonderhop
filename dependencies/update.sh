#!/usr/bin/env bash

# This script mirrors fabfile.py's update command. It gives a shortcut to 
# update (pull, syncdb, migrate, collectstatic, and reload) without using
# Fabric from a local working copy.

set -e

cd "%(proj_root)s"
git pull
./manage.py syncdb --noinput
./manage.py migrate --noinput
./manage.py collectstatic --noinput
sudo service apache2 reload
