#!/usr/bin/bash
#
#
cd server
gunicorn --threads 4 -b 0.0.0.0 'server:app'
