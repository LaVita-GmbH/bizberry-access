from typing import Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from djpykafka.events.subscribe import GenericSubscription
from ...... import models


class Change(BaseModel):
    name: str
    previous_value: Any


class Employee(BaseModel):
    class Type(Enum):
        OWNER = 'OWNER'
        ADMIN = 'ADMIN'

    class Reference(BaseModel):
        id: str

    class Name(BaseModel):
        first: str
        last: str

    id: int
    number: str
    gender: models.User.Gender
    type: Optional[Type]
    name: Name
    email: str
    language: str

    changed: Optional[List[Change]] = Field(alias='_changed')


class Employees(
    GenericSubscription,
    event_schema=Employee,
    topic='odoo.company_reward.employee',
):
    data: Employee

    def process(self):
        print(self.data)
        if not self.data.type:
            return

        email = self.data.email

        if self.data.changed:
            try:
                email = next(filter(lambda c: c.name == 'email', self.data.changed)).previous_value

            except StopIteration:
                pass

        try:
            user: models.User = models.User.objects.get(email=email, tenant_id=self.event.tenant_id)

        except models.User.DoesNotExist:
            try:
                user: models.User = models.User.objects.get(email=self.data.email, tenant_id=self.event.tenant_id)

            except models.User.DoesNotExist:
                user = models.User(email=self.data.email, tenant_id=self.event.tenant_id)

        user.email = self.data.email
        user.first_name = self.data.name.first
        user.last_name = self.data.name.last
        user.gender = self.data.gender
        user.language = self.data.language

        user.save()