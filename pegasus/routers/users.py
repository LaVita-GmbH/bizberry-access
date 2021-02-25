from olympus.utils.pydantic_django import transfer_to_orm
from typing import Dict, List, Optional, Tuple
from asgiref.sync import sync_to_async
from fastapi import APIRouter, Security, Body, Depends, Path, Query
from django.db.models import Q
from olympus.exceptions import AccessError
from olympus.schemas import Access, LimitOffset
from olympus.utils import depends_limit_offset, dict_remove_none
from ..utils import JWTToken
from .. import models
from ..schemas import response, request


router = APIRouter()

transaction_token = JWTToken(scheme_name="Transaction Token")


def access_user(access: Access = Security(transaction_token)) -> Access:
    access.user = models.User.objects.get(id=access.user_id, tenant_id=access.tenant_id)

    return access


def _check_access_for_obj(access: Access, user: models.User, action: Optional[str] = None):
    if access.tenant_id != user.tenant_id:
        raise AccessError

    if access.scope.selector != 'any':
        if user != access.user:
            raise AccessError

        if user.status == models.User.Status.TERMINATED:
            raise AccessError


@sync_to_async
def _get_users_filtered(access: Access, limitoffset: LimitOffset, **filters) -> List[models.User]:
    q_filters = Q(tenant_id=access.tenant_id, **dict_remove_none(filters))
    return list(models.User.objects.filter(q_filters)[limitoffset.offset:limitoffset.limit])


@sync_to_async
def _get_user_by_id(access: Access, user_id: str) -> models.User:
    user = models.User.objects.get(id=user_id)
    _check_access_for_obj(access, user)

    return user


@sync_to_async
def _create_user(access: Access, body: request.UserCreate) -> models.User:
    new_user = models.User.objects.create_user(
        email=str(body.email),
        password=str(body.password.get_secret_value()),
        tenant_id=access.tenant_id,
    )

    return new_user


@sync_to_async
def _delete_user(access: Access, user: models.User):
    _check_access_for_obj(access, user, action='delete')
    user.status = models.User.Status.TERMINATED
    user.save()


@router.post('', response_model=response.User)
async def post_user(
    access: Access = Security(access_user, scopes=['access.users.create',]),
    body: request.UserCreate = Body(...),
):
    """
    Scopes: `access.users.create`
    """
    new_user = await _create_user(access, body)

    response_user = await response.User.from_orm(new_user)
    return response_user


@router.get('', response_model=response.UsersList)
async def get_users(
    access: Access = Security(access_user, scopes=['access.users.read.any']),
    limitoffset: LimitOffset = Depends(depends_limit_offset()),
    status: Optional[models.User.Status] = Query(models.User.Status.ACTIVE),
):
    users: List[models.User] = await _get_users_filtered(access, limitoffset, status=status)

    return response.UsersList(
        users=[await response.User.from_orm(user) for user in users],
    )


@router.get('/self', response_model=response.User)
async def get_self(access: Access = Security(access_user, scopes=['access.users.read.own',])):
    """
    Scopes: `access.users.read.own`
    """
    return await get_user(access=access, user_id=access.user_id)


@router.get('/{user_id}', response_model=response.User)
async def get_user(
    access: Access = Security(access_user, scopes=['access.users.read.any', 'access.users.read.own']),
    user_id: str = Path(...),
):
    """
    Scopes: `access.users.read.any`, `access.users.read.own`
    """
    user = await _get_user_by_id(access, user_id)

    return await response.User.from_orm(user)


@router.patch('/{user_id}', response_model=response.User)
async def patch_user(
    access: Access = Security(access_user, scopes=['access.users.update.any', 'access.users.update.own']),
    user_id: str = Path(...),
    body: request.UserUpdate = Body(...),
):
    user = await _get_user_by_id(access, user_id)

    transfer_to_orm(body, user, exclude_unset=True, access=access)
    await sync_to_async(user.save)()

    return await response.User.from_orm(user)


@router.delete('/{user_id}', status_code=204)
async def delete_user(
    access: Access = Security(access_user, scopes=['access.users.delete.any', 'access.users.delete.own']),
    user_id: str = Path(...),
):
    user = await _get_user_by_id(access, user_id)

    await _delete_user(user)
