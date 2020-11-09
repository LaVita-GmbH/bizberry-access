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
from django.core.exceptions import ObjectDoesNotExist
from fautils.handlers.error import generic_exception_handler, object_does_not_exist_handler
from fautils.middleware.sentry import SentryAsgiMiddleware

from .schemas.response import Health
from fautils.wrappers import wrap_into_response
from fautils.schemas.response import Response


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pegasus.settings')

django_asgi = get_asgi_application()


from . import routers


app = FastAPI(
    title="PEGASUS",
)

@app.get('/health', response_model=Response.wraps(data=Health))
@wrap_into_response
async def healthcheck():
    return Health(status='ok')


app.include_router(routers.auth.router, prefix='/auth', tags=['auth'])
app.include_router(routers.users.router, prefix='/users', tags=['users'])
app.mount('', django_asgi)

app.add_middleware(SentryAsgiMiddleware)

app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(ObjectDoesNotExist, object_does_not_exist_handler)
# app.add_exception_handler(HTTPException, http_exception_handler)
# app.add_exception_handler(RequestValidationError, validation_exception_handler)
