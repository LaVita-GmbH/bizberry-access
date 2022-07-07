from typing import Optional
from pydantic import Field, EmailStr, validator
from djfapi.utils.pydantic_django import DjangoORMBaseModel
from djfapi.validators.language import format_language
from djfapi.utils.pydantic import Reference
from ... import models


class User(DjangoORMBaseModel):
    class RoleReference(Reference, rel='bizberry/access/roles'):
        id: str = Field(orm_field=models.User.role)

    email: EmailStr = Field(orm_field=models.User.email, is_critical=True)
    language: str = Field(orm_field=models.User.language)
    role: Optional[RoleReference] = Field(scopes=['access.users.update.any'], is_critical=True)
    number: Optional[str] = Field(orm_field=models.User.number, scopes=['access.users.update.any'])

    @validator('language')
    def format_language(cls, value: Optional[str]):
        return format_language(value)


class UserFlag(DjangoORMBaseModel):
    key: str = Field(orm_field=models.UserFlag.key)