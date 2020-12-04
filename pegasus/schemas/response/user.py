from enum import Enum
from typing import List, Optional, Set
from pydantic import BaseModel, Field
from ... import models
from . import Role


class User(BaseModel):
    class Status(str, Enum):
        ACTIVE = 'active'
        TERMINATED = 'terminated'

    class RoleTenantRel(Role):
        class TenantReference(BaseModel):
            id: str

        tenant: Optional[TenantReference] = Field(None)

        class Config:
            orm_mode = False

    id: str
    email: str
    status: Status
    roles: List[RoleTenantRel]

    class Config:
        orm_mode = True

    @classmethod
    async def from_orm(cls, obj: models.User, tenant: Optional[str]):
        roles = await obj.get_roles(tenant=tenant)
        values = {
            'id': obj.id,
            'email': obj.email,
            'status': obj.status,
            'roles': [
                cls.RoleTenantRel.parse_obj({
                    'id': role.id,
                    'tenant': {
                        'id': role_tenant.id,
                    } if role_tenant else None,
                }) for role, role_tenant in roles
            ],
        }
        return cls(**values)
