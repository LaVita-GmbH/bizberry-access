from asgiref.sync import sync_to_async
from fastapi import APIRouter, Security, Body
from olympus.schemas import Access
from ..utils import JWTToken
from ..models import Tenant
from ..schemas import response


router = APIRouter()

transaction_token = JWTToken(scheme_name="Transaction Token")


@sync_to_async
def get_tenants_filtered():
    return list(Tenant.objects.all())


@sync_to_async
def get_tenant_by_id(tenant_id: str):
    return Tenant.objects.get(id=tenant_id)


@router.get('', response_model=response.TenantsList)
async def get_tenants():
    tenants = await get_tenants_filtered()
    return response.TenantsList(
        tenants=[
            await response.Tenant.from_orm(tenant)
            for tenant in tenants
        ],
    )


@router.get('/{tenant_id}', response_model=response.Tenant)
async def get_tenant(tenant_id: str):
    tenant = await get_tenant_by_id(tenant_id)

    return await response.Tenant.from_orm(tenant)
