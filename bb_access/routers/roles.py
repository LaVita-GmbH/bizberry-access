from typing import List, Optional

from django.db.models import Q
from fastapi import APIRouter, Security, Depends, Path, Query
from djdantic.utils.dict import remove_none
from djdantic.schemas import Access
from djfapi.schemas import Pagination
from djfapi.utils.fastapi import depends_pagination

from bb_access.utils import JWTToken
from bb_access import models
from bb_access.schemas import response, request


router = APIRouter()

transaction_token = JWTToken(scheme_name="Transaction Token")


def _get_roles_filtered(
    access: Access, pagination: Pagination, *queries, **filters
) -> List[models.Role]:
    q_filters = Q(*queries, **remove_none(filters))
    return list(
        models.Role.objects.filter(q_filters)[pagination.offset : pagination.limit]
    )


def _get_role_by_id(access: Access, role_id: str) -> models.Role:
    return models.Role.objects.get(id=role_id)


@router.get("", response_model=response.RolesList)
def get_roles(
    access: Access = Security(
        transaction_token,
        scopes=[
            "access.roles.read.any",
        ],
    ),
    pagination: Pagination = Depends(depends_pagination()),
    name: Optional[str] = Query(None, max_length=56),
):
    roles = _get_roles_filtered(access, pagination, name=name)
    return response.RolesList(
        roles=[response.Role.from_orm(role) for role in roles],
    )


@router.get("/{role_id}", response_model=response.Role)
def get_role(
    access: Access = Security(
        transaction_token,
        scopes=[
            "access.roles.read.any",
        ],
    ),
    role_id: str = Path(..., min_length=32, max_length=32),
):
    role = _get_role_by_id(access, role_id)

    return response.Role.from_orm(role)
