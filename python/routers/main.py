# routers/main.py
from datetime import timedelta
from typing import Dict, Tuple, Union
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import *
from schemas.search import CursorResponse, SearchRequest, placedetail
from services.search import search_places

from schemas.schedule import (
    ItineraryRequest,
    ItineraryWithAccommodationRequest,
    ItineraryResponse
)
from services.schedule import ItineraryService

router = APIRouter()

# --- 검색 API ---
@router.post("/fastapi/search", response_model=CursorResponse, tags=["Search"], summary="텍스트로 장소 검색")
def search_places_endpoint(req: SearchRequest, db: Session = Depends(get_db)):
    return search_places(db, req.text, req.limit, req.cursor_id)


@router.get("/fastapi/place/{placeId}",response_model=placedetail)
def get_place_detail(placeId: int, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.placeId == placeId).first()
    if not place:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다.")
    return place



# --- 일정 추천 API ---
@router.post(
    "/fastapi/itinerary",
    response_model=ItineraryResponse,
    tags=["itinerary"],
    summary="지역·기간·테마 기반 일정 추천 (숙소 정보 선택적)"
)
def recommend_itinerary(
    req: Union[ItineraryWithAccommodationRequest, ItineraryRequest],
    db: Session = Depends(get_db),
):
    # 1) 여행 기간(days) 계산
    duration = (req.end_date - req.start_date).days + 1

    # 2) 숙소 정보 유무로 분기
    if hasattr(req, "accommodation_coords") and req.accommodation_coords:
        # 숙소 좌표가 있으면 with_accommodation 로직
        daily_itins = ItineraryService.generate_with_accommodation(
            db=db,
            region=req.region,
            theme=req.theme,
            accommodation_coords=req.accommodation_coords,
            start_date=req.start_date,
            duration=duration,
            per_day=req.per_day
        )
    else:
        # 숙소 정보 없으면 without_accommodation 로직
        daily_itins = ItineraryService.generate_without_accommodation(
            db=db,
            region=req.region,
            theme=req.theme,
            start_date=req.start_date,
            duration=duration,
            per_day=req.per_day
        )

    if not daily_itins:
        raise HTTPException(status_code=404, detail="조건에 맞는 여행지가 없습니다.")

    return ItineraryResponse(itinerary=daily_itins)