from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Place as PlaceModel
from schemas.search import Place as PlaceSchema, CursorResponse

def search_places(
    db: Session,
    text: str,
    limit: int = 20,
    cursor_id: Optional[int] = None,
) -> CursorResponse:
    q = db.query(PlaceModel)

    # 1) 텍스트 검색
    if text:
        pattern = f"%{text}%"
        q = q.filter(
            or_(
                PlaceModel.name.ilike(pattern),
                PlaceModel.address.ilike(pattern),
            )
        )

    # 2) 커서 기반 페이징 
    if cursor_id:
        q = q.filter(PlaceModel.placeId < cursor_id)       

    # 3) 정렬 및 조회 (avgRating, placeId 등 실제 속성명 확인)
    results: List[PlaceModel] = (
        q.order_by(
            PlaceModel.avgRating.desc(),                  
            PlaceModel.placeId.desc()
        )
        .limit(limit)
        .all()
    )

    # 4) Pydantic 객체로 변환
    places_out = [PlaceSchema.from_orm(p) for p in results]

    # 5) 다음 커서 계산
    next_cursor = results[-1].placeId if len(results) == limit else None

    return CursorResponse(
        places=places_out,
        next_cursor=next_cursor,           # 이제 int 또는 None
        has_more=bool(next_cursor),
    )