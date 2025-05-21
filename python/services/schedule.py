# services/schedule.py
import numpy as np
from sklearn.cluster import KMeans
from sqlalchemy.orm import Session
from datetime import timedelta
from collections import defaultdict

from models import Itinerary, ScheduleSlot, Place as PlaceModel
from schemas.schedule import DailyItinerary, Place as PlaceSchema


class ItineraryService:

    @staticmethod
    def generate_without_accommodation(
        db: Session,
        region: str,
        theme: str,
        start_date,                # datetime.date
        duration: int,
        per_day: int = 4,
        user_id: int = None,
        preference_id: int = None,
    ) -> list[DailyItinerary]:
        places = (
            db.query(PlaceModel)
              .filter(PlaceModel.address.contains(region))
              .filter(PlaceModel.theme == theme)
              .all()
        )
        if not places:
            return []

        coords = np.array([[float(p.latitude), float(p.longitude)] for p in places])
        total_clusters = min(duration * per_day, len(places))
        kmeans = KMeans(n_clusters=total_clusters, random_state=42).fit(coords)
        labels = kmeans.labels_

        cluster_idxs = defaultdict(list)
        for idx, lbl in enumerate(labels):
            cluster_idxs[lbl].append(idx)

        cluster_scores = []
        for lbl, idxs in cluster_idxs.items():
            scores = [float(getattr(places[i], "avgRating", 0) or 0) for i in idxs]
            avg_score = sum(scores) / len(scores) if scores else 0
            cluster_scores.append((lbl, avg_score))

        sorted_labels = [lbl for lbl, _ in sorted(cluster_scores, key=lambda x: -x[1])]

        # Itinerary 저장
        itin = Itinerary(
            userId=user_id,
            preferenceId=preference_id,
            startDate=start_date,
            endDate=start_date + timedelta(days=duration - 1),
            # createdAt은 server_default로 잡히니 생략 가능하지만 명시해도 됩니다
        )
        db.add(itin)
        db.flush()  # itin.itineraryId 확보

        daily: list[DailyItinerary] = []
        for day in range(duration):
            sel_labels = sorted_labels[day * per_day : day * per_day + per_day]
            idxs = [i for lbl in sel_labels for i in cluster_idxs[lbl]]
            idxs = sorted(
                idxs,
                key=lambda i: -float(getattr(places[i], "avgRating", 0) or 0)
            )[:per_day]

            # 오늘의 장소를 PlaceSchema에 매핑
            places_list = []
            for i in idxs:
                p = places[i]
                places_list.append(
                    PlaceSchema(
                        place_id=p.placeId,
                        name=p.name,
                        theme=p.theme,
                        avg_rating=float(p.avgRating or 0),
                        address=p.address,
                        latitude=float(p.latitude),
                        longitude=float(p.longitude),
                        description=p.description,
                        heritage_type=p.heritageType,
                        info_center=p.infoCenter,
                        closed_day=p.closedDay,
                        experience_info=p.experienceInfo,
                        min_age=p.minAge,
                        business_hours=p.businessHours,
                        parking_info=p.parkingInfo,
                        details=p.details,
                        image=p.image,
                    )
                )
                # ScheduleSlot 저장
                slot = ScheduleSlot(
                    itineraryId=itin.itineraryId,
                    placeId=p.placeId,
                    travelDate=start_date + timedelta(days=day)
                )
                db.add(slot)

            daily.append(DailyItinerary(day=day + 1, places=places_list))

        db.commit()
        return daily


    @staticmethod
    def generate_with_accommodation(
        db: Session,
        region: str,
        theme: str,
        accommodation_coords: dict[int, tuple[float, float]],
        start_date,
        duration: int,
        per_day: int = 4,
        user_id: int = None,
        preference_id: int = None,
    ) -> list[DailyItinerary]:
        base = (
            db.query(PlaceModel)
              .filter(PlaceModel.address.contains(region))
              .filter(PlaceModel.theme == theme)
              .all()
        )
        if not base:
            return []

        itin = Itinerary(
            userId=user_id,
            preferenceId=preference_id,
            startDate=start_date,
            endDate=start_date + timedelta(days=duration - 1),
        )
        db.add(itin)
        db.flush()

        used = set()
        daily: list[DailyItinerary] = []

        for day in range(1, duration + 1):
            center = accommodation_coords.get(day)
            if center:
                lat0, lon0 = center
                cand = [
                    p for p in base
                    if p.placeId not in used
                    and abs(float(p.latitude) - lat0) <= 0.3
                    and abs(float(p.longitude) - lon0) <= 0.3
                ]
            else:
                cand = [p for p in base if p.placeId not in used]

            if not cand:
                daily.append(DailyItinerary(day=day, places=[]))
                continue

            coords = np.array([[float(p.latitude), float(p.longitude)] for p in cand])
            k = min(per_day, len(cand))
            km = KMeans(n_clusters=k, random_state=42).fit(coords)

            chosen_idxs: list[int] = []
            for cluster_idx in range(k):
                pts = np.where(km.labels_ == cluster_idx)[0]
                closest = min(
                    pts, key=lambda i: np.linalg.norm(coords[i] - km.cluster_centers_[cluster_idx])
                )
                chosen_idxs.append(closest)

            places_today: list[PlaceSchema] = []
            for idx in chosen_idxs:
                p = cand[idx]
                used.add(p.placeId)
                slot = ScheduleSlot(
                    itineraryId=itin.itineraryId,
                    placeId=p.placeId,
                    travelDate=start_date + timedelta(days=day - 1)
                )
                db.add(slot)
                places_today.append(
                    PlaceSchema(
                        place_id=p.placeId,
                        name=p.name,
                        theme=p.theme,
                        avg_rating=float(p.avgRating or 0),
                        address=p.address,
                        latitude=float(p.latitude),
                        longitude=float(p.longitude),
                        description=p.description,
                        heritage_type=p.heritageType,
                        info_center=p.infoCenter,
                        closed_day=p.closedDay,
                        experience_info=p.experienceInfo,
                        min_age=p.minAge,
                        business_hours=p.businessHours,
                        parking_info=p.parkingInfo,
                        details=p.details,
                        image=p.image,
                    )
                )

            daily.append(DailyItinerary(day=day, places=places_today))

        db.commit()
        return daily