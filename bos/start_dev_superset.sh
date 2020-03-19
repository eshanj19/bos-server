#!/bin/bash

export PYTHONPATH=/home/eshanjoshi/Maverick-Labs/Code/bos-server/bos/bos/

gunicorn -b 0.0.0.0:8088 superset:app

