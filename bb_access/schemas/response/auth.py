from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from djdantic.utils.pydantic_django import DjangoORMBaseModel
from ... import models


class AuthUserToken(BaseModel):
    user: str


class AuthUser(BaseModel):
    token: AuthUserToken


class AuthTransactionToken(BaseModel):
    transaction: str


class AuthTransaction(BaseModel):
    token: AuthTransactionToken


class AuthOTP(DjangoORMBaseModel):
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
