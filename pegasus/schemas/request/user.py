from typing import List, Optional
from pydantic import BaseModel, EmailStr, SecretStr, Field, validator
from ... import models
from .. import base


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr
    language: str = Field(max_length=8)

    @validator('language')
    def format_language(cls, value: str):
        return base.User.format_language(value)


class UserUpdate(base.User):
    email: Optional[EmailStr] = Field(orm_field=models.User.email, is_critical=True)
    password: Optional[SecretStr] = Field(orm_method=models.User.set_password, is_critical=True)
    language: Optional[str] = Field(orm_field=models.User.language)
    role: Optional[base.User.RoleReference]
