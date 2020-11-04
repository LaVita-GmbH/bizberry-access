"""
ASGI config for pegasus project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fautils.handlers.error import http_exception_handler, validation_exception_handler, generic_exception_handler
from fautils.middleware.sentry import SentryAsgiMiddleware
from . import routers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pegasus.settings')

django_asgi = get_asgi_application()

app = FastAPI()

@app.get('/health')
def healthcheck():
    return {'status': 'ok'}

app.include_router(routers.auth.router, prefix='/auth', tags=['auth'])
app.mount('', django_asgi)

app.add_middleware(SentryAsgiMiddleware)

app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
