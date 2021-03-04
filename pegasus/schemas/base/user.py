from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from olympus.utils import DjangoORMBaseModel
import langcodes
from ... import models


class User(DjangoORMBaseModel):
    class RoleReference(BaseModel):
        id: str = Field(orm_field=models.User.role, scopes=['access.users.update.any'], is_critical=True)

    email: EmailStr = Field(orm_field=models.User.email, is_critical=True)
    language: str = Field(orm_field=models.User.language)

    @validator('language')
    def format_language(cls, value: str):
        lang = langcodes.Language.get(value)

        if not lang.is_valid():
            raise ValueError('language_invalid')

        return lang.simplify_script().to_tag()
