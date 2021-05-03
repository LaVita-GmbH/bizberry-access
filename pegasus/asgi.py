"""
ASGI config for pegasus project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI, Response
from starlette.exceptions import HTTPException
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from jose.exceptions import JOSEError
from olympus.handlers.error import generic_exception_handler, object_does_not_exist_handler, jose_error_handler, http_exception_handler, integrity_error_handler
from olympus.middleware.sentry import SentryAsgiMiddleware
from olympus.utils.health_check import get_health, Health

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pegasus.settings')

django_asgi = get_asgi_application()


from . import routers


app = FastAPI(
    title="PEGASUS",
    openapi_url='/access/openapi.json',
)

@app.get('/', response_model=Health)
async def healthcheck(response: Response):
    return get_health(response)


app.include_router(routers.auth.router, prefix='/access/auth', tags=['auth'])
app.include_router(routers.users.router, prefix='/access/users', tags=['users'])
app.include_router(routers.tenants.router, prefix='/access/tenants', tags=['tenants'])
app.mount('', django_asgi)

app.add_middleware(SentryAsgiMiddleware)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(ObjectDoesNotExist, object_does_not_exist_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(JOSEError, jose_error_handler)
