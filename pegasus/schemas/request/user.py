from typing import List, Optional
from pydantic import BaseModel, EmailStr, SecretStr, Field, validator
from olympus.utils.pydantic import to_optional
from ... import models
from .. import base


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr
    language: str = Field(max_length=8)

    @validator('language')
    def format_language(cls, value: str):
        return base.User.format_language(value)


@to_optional()
class UserUpdate(base.User):
    password: Optional[SecretStr] = Field(orm_method=models.User.set_password, is_critical=True)
