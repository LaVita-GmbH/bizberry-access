from typing import List, Optional
from pydantic import BaseModel, EmailStr, SecretStr, Field, validator
from olympus.utils.pydantic import to_optional
from ... import models
from .. import base


class UserCreate(base.User):
    password: Optional[SecretStr] = ...


@to_optional()
class UserUpdate(base.User):
    password: Optional[SecretStr] = Field(orm_method=models.User.set_password, is_critical=True)


class UserOTPCreate(BaseModel):
    type: models.UserOTP.UserOTPType
    length: Optional[int] = None
    validity: Optional[int] = None
    is_internal: Optional[bool] = True
