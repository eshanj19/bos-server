#!/bin/bash

django-admin makemessages --locale=hi_IN --locale=en_IN --locale=ka_IN
django-admin compilemessages 
