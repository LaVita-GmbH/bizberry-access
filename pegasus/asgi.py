"""
ASGI config for pegasus project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from django.core.exceptions import ObjectDoesNotExist
from jose.exceptions import JOSEError
from olympus.handlers.error import generic_exception_handler, object_does_not_exist_handler, jose_error_handler, http_exception_handler
from olympus.middleware.sentry import SentryAsgiMiddleware
from starlette.exceptions import HTTPException


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pegasus.settings')

django_asgi = get_asgi_application()


from .schemas.response import Health
from . import routers


app = FastAPI(
    title="PEGASUS",
)

@app.get('/health', response_model=Health)
async def healthcheck():
    return Health(status='ok')


app.include_router(routers.auth.router, prefix='/access/auth', tags=['auth'])
app.include_router(routers.users.router, prefix='/access/users', tags=['users'])
app.mount('', django_asgi)

app.add_middleware(SentryAsgiMiddleware)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(ObjectDoesNotExist, object_does_not_exist_handler)
app.add_exception_handler(JOSEError, jose_error_handler)
