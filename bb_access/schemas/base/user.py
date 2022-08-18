from typing import Optional
from pydantic import EmailStr, validator, BaseModel
from djdantic import Field
from djdantic.utils.pydantic_django import DjangoORMBaseModel
from djfapi.validators.language import format_language
from djdantic.utils.pydantic import Reference
from ... import models


class User(DjangoORMBaseModel):
    class RoleReference(Reference, rel='bizberry/access/roles'):
        id: str = Field(orm_field=models.User.role)

    class Name(BaseModel):
        first: str = Field(max_length=150, orm_field=models.User.first_name)
        last: str = Field(max_length=150, orm_field=models.User.last_name)

    email: EmailStr = Field(orm_field=models.User.email, is_critical=True)
    language: str = Field(orm_field=models.User.language)
    role: Optional[RoleReference] = Field(scopes=['access.users.update.any'], is_critical=True)
    number: Optional[str] = Field(orm_field=models.User.number, scopes=['access.users.update.any'])
    name: Optional[Name]

    @validator('language')
    def format_language(cls, value: Optional[str]):
        return format_language(value)


class UserFlag(DjangoORMBaseModel):
    key: str = Field(orm_field=models.UserFlag.key)
