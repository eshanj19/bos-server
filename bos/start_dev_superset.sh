#!/bin/bash

export PYTHONPATH=/home/eshanjoshi/Maverick-Labs/Code/bos-server/bos/bos/

cp bos/dev_superset_config.py bos/superset_config.py
gunicorn -b 0.0.0.0:8088 superset:app

