from typing import Dict, List, Optional, Tuple
from olympus.utils.sync import sync_to_async
from fastapi import APIRouter, Security, Body, Depends, Path, Query
from django.db.models import Q
from olympus.exceptions import AccessError
from olympus.schemas import Access, Pagination
from olympus.utils import depends_pagination, dict_remove_none
from olympus.utils.pydantic_django import transfer_to_orm, TransferAction
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
def _get_users_filtered(access: Access, pagination: Pagination, **filters) -> List[models.User]:
    q_filters = Q(tenant_id=access.tenant_id, **dict_remove_none(filters))
    return list(pagination.query(models.User.objects, q_filters))


@sync_to_async
def _get_user_by_id(access: Access, user_id: str) -> models.User:
    user = models.User.objects.get(id=user_id)
    _check_access_for_obj(access, user)

    return user


@sync_to_async
def _get_user_token_by_id(access: Access, user_id: str, token_id: str) -> models.UserToken:
    token = models.UserToken.objects.get(user_id=user_id, id=token_id)
    _check_access_for_obj(access, token.user)

    return token


@sync_to_async
def _create_user(access: Access, body: request.UserCreate) -> models.User:
    new_user = models.User.objects.create_user(
        email=str(body.email),
        password=body.password and str(body.password.get_secret_value()),
        tenant_id=access.tenant_id,
        language=body.language,
        number=body.number,
        role_id=body.role and body.role.id,
    )

    return new_user


@sync_to_async
def _create_user_access_token(access: Access, user: models.User) -> models.UserAccessToken:
    return user.access_tokens.create()


@sync_to_async
def _create_user_otp(access: Access, user: models.User, body: request.UserOTPCreate) -> models.UserOTP:
    return user.request_otp(
        type=body.type,
        length=body.length,
        validity=body.validity,
        is_internal=False if body.is_internal is False else True,
    )


@sync_to_async
def _delete_user(access: Access, user: models.User):
    _check_access_for_obj(access, user, action='delete')
    user.status = models.User.Status.TERMINATED
    user.save()


@sync_to_async
def _delete_user_token(access: Access, token: models.UserToken):
    token.is_active = False
    token.save()


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
    pagination: Pagination = Depends(depends_pagination()),
    status: Optional[models.User.Status] = Query(models.User.Status.ACTIVE),
    email: Optional[str] = Query(None),
):
    users: List[models.User] = await _get_users_filtered(
        access,
        pagination,
        status=status,
        email=email,
    )

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
    user_id: str = Path(..., min_length=64, max_length=64),
):
    """
    Scopes: `access.users.read.any`, `access.users.read.own`
    """
    user = await _get_user_by_id(access, user_id)

    return await response.User.from_orm(user)


@router.patch('/{user_id}', response_model=response.User)
async def patch_user(
    access: Access = Security(access_user, scopes=['access.users.update.any', 'access.users.update.own']),
    user_id: str = Path(..., min_length=64, max_length=64),
    body: request.UserUpdate = Body(...),
):
    user = await _get_user_by_id(access, user_id)

    await transfer_to_orm(body, user, exclude_unset=True, access=access, action=TransferAction.NO_SUBOBJECTS)

    return await response.User.from_orm(user)


@router.delete('/{user_id}', status_code=204)
async def delete_user(
    access: Access = Security(access_user, scopes=['access.users.delete.any', 'access.users.delete.own']),
    user_id: str = Path(..., min_length=64, max_length=64),
):
    user = await _get_user_by_id(access, user_id)

    await _delete_user(access, user)


@router.delete('/{user_id}/tokens/{token_id}', status_code=204)
async def delete_user_token(
    access: Access = Security(access_user, scopes=['access.users.update.any', 'access.users.read.own']),
    user_id: str = Path(..., min_length=64, max_length=64),
    token_id: str = Path(..., min_length=128, max_length=128),
):
    token = await _get_user_token_by_id(access, user_id, token_id)

    await _delete_user_token(access, token)


@router.post('/{user_id}/access-token', response_model=response.UserAccessToken)
async def post_user_access_token(
    access: Access = Security(access_user, scopes=['access.users.create_access_token.any', 'access.users.create_access_token.own']),
    user_id: str = Path(..., min_length=64, max_length=64),
):
    user = await _get_user_by_id(access, user_id)
    access_token = await _create_user_access_token(access, user)

    return await response.UserAccessToken.from_orm(access_token)


@router.post('/{user_id}/otp', response_model=response.UserOTP)
async def post_user_otp(
    access: Access = Security(access_user, scopes=['access.users.create_otp.any',]),
    user_id: str = Path(..., min_length=64, max_length=64),
    body: request.UserOTPCreate = Body(...),
):
    user = await _get_user_by_id(access, user_id)
    otp: models.UserOTP = await _create_user_otp(access, user, body)

    return response.UserOTP(token=otp._value)
