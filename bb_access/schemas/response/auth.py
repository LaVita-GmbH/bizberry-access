from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from djdantic import Field, BaseModel

from bb_access import models


class AuthUserToken(BaseModel):
    user: str


class AuthUser(BaseModel):
    token: AuthUserToken
    via: models.User.LoginMethod


class AuthTransactionToken(BaseModel):
    transaction: str


class AuthTransaction(BaseModel):
    token: AuthTransactionToken


class AuthOTP(BaseModel):
    id: str = Field(orm_field=models.UserOTP.id)
    type: models.UserOTP.UserOTPType = Field(orm_field=models.UserOTP.type)
    created_at: datetime = Field(orm_field=models.UserOTP.created_at)
    expire_at: datetime = Field(orm_field=models.UserOTP.expire_at)
    length: int = Field(orm_field=models.UserOTP.length)


class AuthCheck(BaseModel):
    class Email(BaseModel):
        is_valid: bool
        is_existing: bool

    email: Optional[Email]
