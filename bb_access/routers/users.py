from typing import List, Optional

from fastapi import APIRouter, Security, Body, Depends, Path, Query, Response
from django.db.models import Q
from djdantic.exceptions import AccessError
from djdantic.utils.dict import remove_none
from djdantic.utils.pydantic_django import transfer_to_orm, TransferAction
from djdantic.schemas import Access
from djfapi.schemas import Pagination
from djfapi.utils.fastapi import depends_pagination

from bb_access.utils import JWTToken
from bb_access import models
from bb_access.schemas import response, request


router = APIRouter()

transaction_token = JWTToken(scheme_name="Transaction Token")


def access_user(access: Access = Security(transaction_token)) -> Access:
    access.user = models.User.objects.get(id=access.user_id, tenant_id=access.tenant_id)

    return access


def _check_access_for_obj(
    access: Access, user: models.User, action: Optional[str] = None
):
    if access.tenant_id != user.tenant_id:
        raise AccessError

    if access.scope.selector != "any":
        if user != access.user:
            raise AccessError

        if user.status == models.User.Status.TERMINATED:
            raise AccessError


def _get_users_filtered(
    access: Access, pagination: Pagination, **filters
) -> List[models.User]:
    q_filters = Q(tenant_id=access.tenant_id, **remove_none(filters))
    return list(pagination.query(models.User.objects, q_filters))


def _get_user_flags_filtered(
    access: Access, user: models.User, pagination: Pagination, **filters
) -> List[models.UserFlag]:
    q_filters = Q(**remove_none(filters))
    return list(pagination.query(user.flags, q_filters))


def _get_user_by_id(access: Access, user_id: str) -> models.User:
    user = models.User.objects.get(id=user_id)
    _check_access_for_obj(access, user)

    return user


def _get_user_token_by_id(
    access: Access, user_id: str, token_id: str
) -> models.UserToken:
    token = models.UserToken.objects.get(user_id=user_id, id=token_id)
    _check_access_for_obj(access, token.user)

    return token


def _get_user_flag(access: Access, user: models.User, flag_key: str) -> models.UserFlag:
    return user.flags.get(key=flag_key)


def _create_user_otp(
    access: Access, user: models.User, body: request.UserOTPCreate
) -> models.UserOTP:
    return user.request_otp(
        type=body.type,
        length=body.length,
        validity=body.validity,
        is_internal=False if body.is_internal is False else True,
    )


def _create_user_flag(
    access: Access, user: models.User, body: request.UserFlagCreate
) -> models.UserFlag:
    user_flag = models.UserFlag(user=user)
    transfer_to_orm(body, user_flag, action=TransferAction.CREATE)

    return user_flag


def _delete_user(access: Access, user: models.User):
    _check_access_for_obj(access, user, action="delete")
    user.status = models.User.Status.TERMINATED
    user.save()


@router.post("", response_model=response.User)
def post_user(
    access: Access = Security(
        access_user,
        scopes=[
            "access.users.create",
        ],
    ),
    body: request.UserCreate = Body(...),
):
    """
    Scopes: `access.users.create`
    """
    user = models.User.objects.create_user(
        email=str(body.email),
        password=body.password and str(body.password.get_secret_value()),
        tenant_id=access.tenant_id,
        language=body.language,
        number=body.number,
        role_id=body.role and body.role.id,
        first_name=body.name.first,
        last_name=body.name.last,
    )

    return response.User.from_orm(user)


@router.get("", response_model=response.UsersList)
def get_users(
    resp: Response,
    access: Access = Security(access_user, scopes=["access.users.read.any"]),
    pagination: Pagination = Depends(depends_pagination()),
    status: Optional[models.User.Status] = Query(models.User.Status.ACTIVE),
    email: Optional[str] = Query(None),
    number: Optional[str] = Query(None),
):
    resp.headers["Cache-Control"] = "no-cache"
    users: List[models.User] = _get_users_filtered(
        access,
        pagination,
        status=status,
        email=email and email.lower(),
        number=number,
    )

    return response.UsersList(
        users=[response.User.from_orm(user) for user in users],
    )


@router.get("/self", response_model=response.User)
def get_self(
    resp: Response,
    access: Access = Security(
        access_user,
        scopes=[
            "access.users.read.own",
        ],
    ),
):
    """
    Scopes: `access.users.read.own`
    """
    return get_user(resp=resp, access=access, user_id=access.user_id)


@router.get("/{user_id}", response_model=response.User)
def get_user(
    resp: Response,
    access: Access = Security(
        access_user, scopes=["access.users.read.any", "access.users.read.own"]
    ),
    user_id: str = Path(..., min_length=64, max_length=64),
):
    """
    Scopes: `access.users.read.any`, `access.users.read.own`
    """
    resp.headers["Cache-Control"] = "no-cache"
    user = _get_user_by_id(access, user_id)

    return response.User.from_orm(user)


@router.patch("/{user_id}", response_model=response.User)
def patch_user(
    access: Access = Security(
        access_user, scopes=["access.users.update.any", "access.users.update.own"]
    ),
    user_id: str = Path(..., min_length=64, max_length=64),
    body: request.UserUpdate = Body(...),
):
    user = _get_user_by_id(access, user_id)

    transfer_to_orm(
        body,
        user,
        exclude_unset=True,
        access=access,
        action=TransferAction.NO_SUBOBJECTS,
    )

    return response.User.from_orm(user)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    access: Access = Security(
        access_user, scopes=["access.users.delete.any", "access.users.delete.own"]
    ),
    user_id: str = Path(..., min_length=64, max_length=64),
):
    user = _get_user_by_id(access, user_id)

    _delete_user(access, user)


@router.delete("/{user_id}/tokens/{token_id}", status_code=204)
def delete_user_token(
    access: Access = Security(
        access_user, scopes=["access.users.update.any", "access.users.read.own"]
    ),
    user_id: str = Path(..., min_length=64, max_length=64),
    token_id: str = Path(..., min_length=128, max_length=128),
):
    token = _get_user_token_by_id(access, user_id, token_id)
    token.is_active = False
    token.save()


@router.post("/{user_id}/access-token", response_model=response.UserAccessToken)
def post_user_access_token(
    access: Access = Security(
        access_user,
        scopes=[
            "access.users.create_access_token.any",
            "access.users.create_access_token.own",
        ],
    ),
    user_id: str = Path(..., min_length=64, max_length=64),
):
    user = _get_user_by_id(access, user_id)
    access_token = user.access_tokens.create()

    return response.UserAccessToken.from_orm(access_token)


@router.post("/{user_id}/otp", response_model=response.UserOTP)
def post_user_otp(
    access: Access = Security(
        access_user,
        scopes=[
            "access.users.create_otp.any",
        ],
    ),
    user_id: str = Path(..., min_length=64, max_length=64),
    body: request.UserOTPCreate = Body(...),
):
    user = _get_user_by_id(access, user_id)
    otp: models.UserOTP = _create_user_otp(access, user, body)

    return response.UserOTP(token=otp._value)


@router.get("/{user_id}/flags", response_model=response.UserFlag)
def get_user_flags(
    resp: Response,
    access: Access = Security(
        access_user,
        scopes=[
            "access.users.read.any",
        ],
    ),
    user_id: str = Path(..., min_length=64, max_length=64),
    key: Optional[str] = Query(None, max_length=64),
):
    resp.headers["Cache-Control"] = "no-cache"
    user = _get_user_by_id(access, user_id)
    flags: List[models.UserFlag] = _get_user_flags_filtered(
        access,
        user,
        key=key,
    )

    return response.UserFlagsList(
        flags=[response.UserFlag.from_orm(flag) for flag in flags],
    )


@router.post("/{user_id}/flags", response_model=response.UserFlag)
def post_user_flag(
    access: Access = Security(
        access_user,
        scopes=[
            "access.users.update.any",
        ],
    ),
    user_id: str = Path(..., min_length=64, max_length=64),
    body: request.UserFlagCreate = Body(...),
):
    user = _get_user_by_id(access, user_id)
    flag: models.UserFlag = _create_user_flag(access, user, body)

    return response.UserFlag.from_orm(flag)


@router.get("/{user_id}/flags/{flag_key}", response_model=response.UserFlag)
def get_user_flag_by_key(
    resp: Response,
    access: Access = Security(
        access_user,
        scopes=[
            "access.users.read.any",
        ],
    ),
    user_id: str = Path(..., min_length=64, max_length=64),
    flag_key: str = Path(..., max_length=64),
):
    resp.headers["Cache-Control"] = "no-cache"
    user = _get_user_by_id(access, user_id)
    flag: models.UserFlag = _get_user_flag(access, user, flag_key)

    return response.UserFlag.from_orm(flag)


@router.delete("/{user_id}/flags/{flag_key}", status_code=204)
def delete_user_flag_by_key(
    access: Access = Security(
        access_user,
        scopes=[
            "access.users.update.any",
        ],
    ),
    user_id: str = Path(..., min_length=64, max_length=64),
    flag_key: str = Path(..., max_length=64),
):
    user = _get_user_by_id(access, user_id)
    flag: models.UserFlag = _get_user_flag(access, user, flag_key)
    flag.delete()
