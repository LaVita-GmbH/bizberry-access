from typing import Optional
from pydantic import BaseModel, Field, validator, EmailStr
from . import TenantReference
from ... import models


class AuthUser(BaseModel):
    class OTP(BaseModel):
        id: str = Field(min_length=64, max_length=64)
        value: str

    email: Optional[str]
    otp: Optional[OTP]
    password: str
    tenant: TenantReference

    @validator('otp')
    def check_email_or_otp(cls, value, values):
        if values.get('email') and values.get('otp'):
            raise ValueError('multiple_values_set:email|otp')

        if not values.get('email') and not values.get('otp'):
            raise ValueError('no_values_set:email|otp')

        return value


class AuthUserReset(BaseModel):
    email: str
    tenant: TenantReference
    type: models.UserOTP.UserOTPType


class AuthTransaction(BaseModel):
    include_critical: bool = Field(False, description="Include critical scopes in the token. To obtain a transaction token with critical scopes using an user token, the token may not be issued more than 1 hour in the past.")
    access_token: Optional[str] = None

    class Config:
        schema_extra = {
            'example': {
                'include_critical': False,
                'access_token': None,
            },
        }


class AuthCheck(BaseModel):
    email: Optional[EmailStr]
