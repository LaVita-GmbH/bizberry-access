from olympus.utils.pydantic_django import transfer_to_orm
from typing import List
from asgiref.sync import sync_to_async
from fastapi import APIRouter, Security, Body, Depends
from olympus.schemas import Access, LimitOffset
from olympus.utils import depends_limit_offset
from ..utils import JWTToken
from ..models import Tenant, TenantCountry
from ..schemas import response, request


router = APIRouter()

transaction_token = JWTToken(scheme_name="Transaction Token")


@sync_to_async
def _get_tenants_filtered(limitoffset: LimitOffset) -> List[Tenant]:
    return list(Tenant.objects.all()[limitoffset.offset:limitoffset.limit])


@sync_to_async
def _get_tenant_by_id(tenant_id: str) -> Tenant:
    return Tenant.objects.get(id=tenant_id)


@sync_to_async
def _get_tenant_countries_filtered(tenant: Tenant, limitoffset: LimitOffset) -> List[TenantCountry]:
    return list(tenant.countries.all()[limitoffset.offset:limitoffset.limit])


@sync_to_async
def _create_tenant_country(tenant: Tenant, body: request.TenantCountryCreate) -> TenantCountry:
    return tenant.countries.create(
        code=body.code,
    )


@sync_to_async
def _tenant_update(tenant: Tenant, body: request.TenantUpdate) -> Tenant:
    transfer_to_orm(body, tenant)
    tenant.save()


@router.get('', response_model=response.TenantsList)
async def get_tenants(
    limitoffset: LimitOffset = Depends(depends_limit_offset()),
):
    tenants = await _get_tenants_filtered(limitoffset)
    return response.TenantsList(
        tenants=[
            await response.Tenant.from_orm(tenant)
            for tenant in tenants
        ],
    )


@router.get('/{tenant_id}', response_model=response.Tenant)
async def get_tenant(tenant_id: str):
    tenant = await _get_tenant_by_id(tenant_id)

    return await response.Tenant.from_orm(tenant)


@router.patch('/{tenant_id}', response_model=response.Tenant)
async def patch_tenant(
    tenant_id: str,
    access: Access = Security(transaction_token, scopes=['access.tenants.update',]),
    body: request.TenantUpdate = Body(...),
):
    """
    Scopes: `access.tenants.update`
    """
    tenant = await _get_tenant_by_id(tenant_id)

    await _tenant_update(tenant, body=body)

    return await response.Tenant.from_orm(tenant)


@router.post('/{tenant_id}/countries', response_model=response.TenantCountry)
async def create_tenant_country(
    tenant_id: str,
    access: Access = Security(transaction_token, scopes=['access.tenants.update',]),
    body: request.TenantCountryCreate = Body(...),
):
    """
    Scopes: `access.tenants.update`
    """
    tenant = await _get_tenant_by_id(tenant_id)
    country = await _create_tenant_country(tenant, body)
    return await response.TenantCountry.from_orm(country)


@router.get('/{tenant_id}/countries', response_model=response.TenantCountriesList)
async def get_tenant_countries(
    tenant_id: str,
    limitoffset: LimitOffset = Depends(depends_limit_offset()),
):
    tenant = await _get_tenant_by_id(tenant_id)
    countries = await _get_tenant_countries_filtered(tenant, limitoffset)

    return response.TenantCountriesList(
        countries=[
            await response.TenantCountry.from_orm(country)
            for country in countries
        ],
    )
