# schemas/search.py
from typing import List, Optional
from pydantic import BaseModel


class SearchRequest(BaseModel):
    text: str
    limit: int = 20 
    cursor_id: Optional[int] = None


class Place(BaseModel):
    placeId: int
    name: str
    theme: str
    avgRating: float
    address: str
    latitude: float
    longitude: float
    description: Optional[str] = None
    heritageType: Optional[str] = None
    infoCenter: Optional[str] = None
    closedDay: Optional[str] = None
    experienceInfo: Optional[str] = None
    minAge: Optional[str] = None
    businessHours: Optional[str] = None
    parkingInfo: Optional[str] = None
    details: Optional[str] = None
    image: Optional[str] = None

    class Config:
        from_attributes=True

class CursorResponse(BaseModel):
    places: List[Place]
    next_cursor: Optional[int] = None
    has_more: bool
    
    
class placedetail(BaseModel):
    placeId: int
    name: str
    theme: str
    avgRating: float
    address: str
    description: Optional[str] = None
    heritageType: Optional[str] = None
    infoCenter: Optional[str] = None
    closedDay: Optional[str] = None
    experienceInfo: Optional[str] = None
    minAge: Optional[str] = None
    businessHours: Optional[str] = None
    parkingInfo: Optional[str] = None
    details: Optional[str] = None
    image: Optional[str] = None

    class Config:
        from_attributes=True