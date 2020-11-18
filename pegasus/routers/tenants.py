from typing import List
from asgiref.sync import sync_to_async
from fastapi import APIRouter, Security, Body
from olympus.schemas import Access
from ..utils import JWTToken
from ..models import Tenant, TenantCountry
from ..schemas import response, request


router = APIRouter()

transaction_token = JWTToken(scheme_name="Transaction Token")


@sync_to_async
def tenants_filtered() -> List[Tenant]:
    return list(Tenant.objects.all())


@sync_to_async
def tenant_by_id(tenant_id: str) -> Tenant:
    return Tenant.objects.get(id=tenant_id)


@sync_to_async
def tenant_countries(tenant: Tenant) -> List[TenantCountry]:
    return list(tenant.countries.all())


@sync_to_async
def tenant_country_create(tenant: Tenant, body: request.TenantCountryCreate) -> TenantCountry:
    return tenant.countries.create(
        code=body.code,
    )


@sync_to_async
def tenant_edit(tenant: Tenant, body: request.TenantPatch) -> Tenant:
    return tenant


@router.get('', response_model=response.TenantsList)
async def get_tenants():
    tenants = await tenants_filtered()
    return response.TenantsList(
        tenants=[
            await response.Tenant.from_orm(tenant)
            for tenant in tenants
        ],
    )


@router.get('/{tenant_id}', response_model=response.Tenant)
async def get_tenant(tenant_id: str):
    tenant = await tenant_by_id(tenant_id)

    return await response.Tenant.from_orm(tenant)


@router.patch('/{tenant_id}', response_model=response.Tenant)
async def patch_tenant(tenant_id: str, access: Access = Security(transaction_token, scopes=['pegasus.tenants.edit',]), body: request.TenantPatch = Body(...)):
    tenant = await tenant_by_id(tenant_id)

    await tenant_edit(tenant, body=body)

    return await response.Tenant.from_orm(tenant)


@router.post('/{tenant_id}/countries', response_model=response.TenantCountry)
async def create_tenant_country(tenant_id: str, access: Access = Security(transaction_token, scopes=['pegasus.tenants.edit',]), body: request.TenantCountryCreate = Body(...)):
    tenant = await tenant_by_id(tenant_id)
    country = await tenant_country_create(tenant, body)
    return await response.TenantCountry.from_orm(country)


@router.get('/{tenant_id}/countries', response_model=response.TenantCountriesList)
async def get_tenant_countries(tenant_id: str):
    tenant = await tenant_by_id(tenant_id)
    countries = await tenant_countries(tenant)

    return response.TenantCountriesList(
        countries=[
            await response.TenantCountry.from_orm(country)
            for country in countries
        ],
    )
