from typing import Any
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declarative_mixin, declared_attr
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Boolean, DateTime

from datetime import datetime
import pytz

def get_current_date():
    # Definir la zona horaria de Chile
    chile_timezone = pytz.timezone('America/Santiago')
    # Obtener la fecha y hora actual en la zona horaria de Chile
    now_in_chile = datetime.now(chile_timezone)
    return now_in_chile




@as_declarative()
class Base:
    id: Any

    def as_dict(self):
        return dict((c.name,
                     getattr(self, c.name))
                    for c in self.__table__.columns)


@declarative_mixin
class SoftDeleteMixin:
    @declared_attr
    def is_deleted(cls):
        return Column(Boolean, nullable=False, server_default='0', default=False)


@declarative_mixin
class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True),
                      nullable=False, server_default=func.now(), default=get_current_date)

    @declared_attr
    def update_at(cls):
        return Column(DateTime(timezone=True),
                      onupdate=func.now(), server_default=func.now(), default=get_current_date)
