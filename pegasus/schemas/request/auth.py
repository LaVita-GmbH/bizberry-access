from typing import Optional
from pydantic import BaseModel


class AuthUser(BaseModel):
    username: Optional[str]
    password: str
