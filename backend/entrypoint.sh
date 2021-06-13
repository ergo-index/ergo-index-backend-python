#!/bin/bash -x

python3 manage.py migrate --noinput
exec "$@"