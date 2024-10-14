from typing import List, Any
from pydantic import BaseModel


class GetPaginated(BaseModel):
    filters: dict
    table_filters: dict
    joins: List[Any]
    options: List[Any]
    pag_params: Any
    db: Any
    order: str
    request: Any = None
