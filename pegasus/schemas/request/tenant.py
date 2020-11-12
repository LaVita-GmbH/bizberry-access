from pydantic import BaseModel


class TenantReference(BaseModel):
    id: str
