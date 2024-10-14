from ...helpers.schema import Base


class MotiveBase(Base):
    name: str
    description: str

class MotiveItem(MotiveBase):
    id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "LACK_OF_INFO",
                "description": "Falta de información",
            
            }
        }


        