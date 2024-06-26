"""
ASGI config for bb_access project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from fastapi import FastAPI, Response
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
from fastapi.encoders import jsonable_encoder
from asyncapi_docgen.docs import get_asyncapi_ui_html
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from jose.exceptions import JOSEError
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bb_access.settings")

django_asgi = get_asgi_application()


from djpykafka.docs.asyncapi import get_asyncapi
from djfapi.handlers.error import (
    generic_exception_handler,
    object_does_not_exist_handler,
    jose_error_handler,
    http_exception_handler,
    integrity_error_handler,
)
from djfapi.middleware.sentry import SentryAsgiMiddleware
from djfapi.utils.health_check import get_health, Health
from . import routers


def asyncapi_html(request):
    return HTMLResponse(get_asyncapi_ui_html(asyncapi_url="/access/asyncapi.json"))


def asyncapi_json(request):
    return JSONResponse(
        jsonable_encoder(get_asyncapi(), by_alias=True, exclude_none=True)
    )


app = FastAPI(
    title="bb_access",
    openapi_url="/access/openapi.json",
    routes=[
        Route("/access/asyncapi", asyncapi_html),
        Route("/access/asyncapi.json", asyncapi_json),
    ],
)


@app.get("/", response_model=Health)
async def healthcheck(response: Response):
    return get_health(response)


app.include_router(routers.auth.router, prefix="/access/auth", tags=["auth"])
app.include_router(routers.users.router, prefix="/access/users", tags=["users"])
app.include_router(routers.roles.router, prefix="/access/roles", tags=["roles"])
app.include_router(routers.tenants.router, prefix="/access/tenants", tags=["tenants"])

app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(ObjectDoesNotExist, object_does_not_exist_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(JOSEError, jose_error_handler)
