# schemas/schedule.py
from datetime import date
from typing import List, Optional, Dict, Tuple
from pydantic import BaseModel


class Place(BaseModel):
    place_id:      int
    name:          str
    theme:         str
    avg_rating:    float
    address:       str
    latitude:      float
    longitude:     float
    description:   Optional[str] = None
    heritage_type: Optional[str] = None
    info_center:   Optional[str] = None
    closed_day:    Optional[str] = None
    experience_info: Optional[str] = None
    min_age:       Optional[str] = None
    business_hours: Optional[str] = None
    parking_info:  Optional[str] = None
    details:       Optional[str] = None
    image:         Optional[str] = None

    class Config:
        from_attributes=True


class DailyItinerary(BaseModel):
    day:    int
    places: List[Place]


class ItineraryResponse(BaseModel):
    itinerary: List[DailyItinerary]


class ItineraryRequest(BaseModel):
    region:     str
    theme:      str
    start_date: date
    end_date:   date
    per_day:    int = 4


class ItineraryWithAccommodationRequest(ItineraryRequest):
    accommodation_coords: Dict[int, Tuple[float, float]]