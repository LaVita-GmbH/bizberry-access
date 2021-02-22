from pydantic import BaseModel, Field, EmailStr
from olympus.utils import DjangoORMBaseModel
from ... import models


class User(DjangoORMBaseModel):
    class RoleReference(BaseModel):
        id: str = Field(orm_field=models.User.role, scopes=['access.users.update.any'])

    email: EmailStr = Field(orm_field=models.User.email)
