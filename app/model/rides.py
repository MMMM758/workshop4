from typing import Optional, List
from pydantic import BaseModel, Field


class createRidesModel(BaseModel):
    id: str = Field(min_length=10, max_length=10)
    menupark_type: str
    rides_name: str
    price: int
    picture_url: str


class updateRidesModel(BaseModel):
    menupark_type: Optional[str]
    rides_name: Optional[str]
    price: Optional[int]
    picture_url: Optional[str]