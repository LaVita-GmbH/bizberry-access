from typing import List, Optional
from pydantic import BaseModel, EmailStr, SecretStr, Field
from ... import models
from .. import base


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr


class UserUpdate(base.User):
    email: Optional[EmailStr] = Field(orm_field=models.User.email)
    password: Optional[SecretStr] = Field(orm_method=models.User.set_password)
    role: Optional[base.User.RoleReference]
