from django.conf import settings
from djfapi.security.jwt import JWTToken as BaseJWTToken


class JWTToken(BaseJWTToken):
    def __init__(self, **kwargs):
        kwargs.setdefault('issuer', settings.JWT_ISSUER)
        kwargs.setdefault('key', settings.JWT_PUBLIC_KEY)
        kwargs.setdefault('algorithm', 'ES512')
        super().__init__(**kwargs)
