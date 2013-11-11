import os
import sys

path = '/home/jonas/git/ppbe-finance/'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'finance.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

