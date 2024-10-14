
from pydantic import BaseModel as PydanicBaseModel


class Base(PydanicBaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
