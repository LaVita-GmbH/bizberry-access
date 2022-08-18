import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bb_access.settings')
os.environ.setdefault('EVENT_CONSUMER_APP_CONFIG', 'django.conf.settings')

django.setup(set_prefix=False)


from ._consumer import consumer
from . import odoo


consumer.run()
