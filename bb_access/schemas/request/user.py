from typing import List, Optional
from pydantic import SecretStr
from djdantic import BaseModel, Field
from djdantic.utils.pydantic import to_optional
from ... import models
from .. import base


class UserCreate(base.User):
    password: Optional[SecretStr] = ...
    flags: Optional[List['UserFlagCreate']] = Field(orm_field=models.User.flags, scopes=['access.users.update.any'])


@to_optional()
class UserUpdate(base.User):
    password: Optional[SecretStr] = Field(orm_method=models.User.set_password, is_critical=True)


class UserOTPCreate(BaseModel):
    type: models.UserOTP.UserOTPType
    length: Optional[int] = None
    validity: Optional[int] = None
    is_internal: Optional[bool] = True


class UserFlagCreate(base.UserFlag):
    pass


UserCreate.update_forward_refs()
