from typing import Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from djpykafka.events.subscribe import GenericSubscription, DataChangeEvent
from django.db.models import Q
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
        if not self.data.type and self.data.changed and not getattr(next(filter(lambda c: c.name == 'type', self.data.changed), None), 'previous_value', None):
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
                user.set_unusable_password()

        if self.event.data_op == DataChangeEvent.DataOperation.DELETE or not self.data.type:
            user.delete()

        else:
            if other_user := models.User.objects.filter(Q(email=self.data.email) & ~Q(id=user.id)).first():
                other_user.delete()

            user.email = self.data.email
            user.first_name = self.data.name.first
            user.last_name = self.data.name.last
            user.gender = self.data.gender
            user.language = self.data.language

            user.save()
