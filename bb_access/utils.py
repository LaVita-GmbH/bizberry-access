from typing import Optional
from django.conf import settings
from djfapi.security.jwt import JWTToken as BaseJWTToken
from rest_client import Style2019ConsumerClient


_odoo_shop_client = {}


class JWTToken(BaseJWTToken):
    def __init__(self, **kwargs):
        kwargs.setdefault('issuer', settings.JWT_ISSUER)
        kwargs.setdefault('key', settings.JWT_PUBLIC_KEY)
        kwargs.setdefault('algorithm', 'ES512')
        super().__init__(**kwargs)


def get_odoo_shop_client(tenant_id) -> Optional[Style2019ConsumerClient]:
    global _odoo_shop_client
    if tenant_id not in _odoo_shop_client:
        config = settings.EXT_CLIENTS.get('odoo_shop', {}).get(tenant_id)
        if not config:
            _odoo_shop_client[tenant_id] = None

        else:
            _odoo_shop_client[tenant_id] = Style2019ConsumerClient(
                **config,
                password_field='password',
            )

    return _odoo_shop_client[tenant_id]
