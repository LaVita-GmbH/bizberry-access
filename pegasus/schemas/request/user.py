from typing import List
from pydantic import BaseModel, EmailStr, SecretStr
from . import RoleReference


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr
