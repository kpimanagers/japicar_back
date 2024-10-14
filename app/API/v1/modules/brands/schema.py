from pydantic import Field
from typing import Optional
from datetime import datetime

from ...helpers.schema import Base


class BrandBase(Base):
    name: str

class BrandItem(BrandBase):
    id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Toyota",

            }
        }


class ModelBase(Base):
    name: str
    brand_id: int = Field(alias="brandId")
    start_year_range: int = Field(alias="startYearRange")
    end_year_range: int = Field(alias="endYearRange")

class ModelItem(ModelBase):
    id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "yaris",
                "brandId": 1,
                "startYearRange": 2000,
                "endYearRange": 2020,

            }
        }


        