from typing import List
from async_tools import sync_to_async
from fastapi import APIRouter, Security, Body, Depends
from djdantic.utils.pydantic_django import transfer_to_orm, TransferAction
from djdantic.schemas import Access
from djfapi.schemas import Pagination
from djfapi.utils.fastapi import depends_pagination
from ..utils import JWTToken
from ..models import Tenant, TenantCountry
from ..schemas import response, request


router = APIRouter()

transaction_token = JWTToken(scheme_name="Transaction Token")


def _get_tenants_filtered(pagination: Pagination) -> List[Tenant]:
    return list(Tenant.objects.all()[pagination.offset:pagination.limit])


def _get_tenant_by_id(tenant_id: str) -> Tenant:
    return Tenant.objects.get(id=tenant_id)


def _get_tenant_countries_filtered(tenant: Tenant, pagination: Pagination) -> List[TenantCountry]:
    return list(tenant.countries.all()[pagination.offset:pagination.limit])


def _create_tenant_country(tenant: Tenant, body: request.TenantCountryCreate) -> TenantCountry:
    return tenant.countries.create(
        code=body.code,
    )


def _tenant_update(tenant: Tenant, body: request.TenantUpdate) -> Tenant:
    transfer_to_orm(body, tenant, action=TransferAction.CREATE)


@router.get('', response_model=response.TenantsList)
def get_tenants(
    pagination: Pagination = Depends(depends_pagination()),
):
    tenants = _get_tenants_filtered(pagination)
    return response.TenantsList(
        tenants=[
            response.Tenant.from_orm(tenant)
            for tenant in tenants
        ],
    )


@router.get('/{tenant_id}', response_model=response.Tenant)
def get_tenant(tenant_id: str):
    tenant = _get_tenant_by_id(tenant_id)

    return response.Tenant.from_orm(tenant)


@router.patch('/{tenant_id}', response_model=response.Tenant)
def patch_tenant(
    tenant_id: str,
    access: Access = Security(transaction_token, scopes=['access.tenants.update',]),
    body: request.TenantUpdate = Body(...),
):
    """
    Scopes: `access.tenants.update`
    """
    tenant = _get_tenant_by_id(tenant_id)

    _tenant_update(tenant, body=body)

    return response.Tenant.from_orm(tenant)


@router.post('/{tenant_id}/countries', response_model=response.TenantCountry)
def create_tenant_country(
    tenant_id: str,
    access: Access = Security(transaction_token, scopes=['access.tenants.update',]),
    body: request.TenantCountryCreate = Body(...),
):
    """
    Scopes: `access.tenants.update`
    """
    tenant = _get_tenant_by_id(tenant_id)
    country = _create_tenant_country(tenant, body)
    return response.TenantCountry.from_orm(country)


@router.get('/{tenant_id}/countries', response_model=response.TenantCountriesList)
def get_tenant_countries(
    tenant_id: str,
    pagination: Pagination = Depends(depends_pagination()),
):
    tenant = _get_tenant_by_id(tenant_id)
    countries = _get_tenant_countries_filtered(tenant, pagination)

    return response.TenantCountriesList(
        countries=[
            response.TenantCountry.from_orm(country)
            for country in countries
        ],
    )
