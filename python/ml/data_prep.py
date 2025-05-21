# ml/data_prep.py
import pandas as pd
import requests
import time
from pathlib import Path
from sqlalchemy import create_engine

BASE_DIR       = Path(__file__).resolve().parent
INPUT_FILE     = BASE_DIR / "curlist.xlsx"
OUTPUT_FILE    = BASE_DIR / "curlist_prep.xlsx"
GOOGLE_API_KEY = "AIzaSyBSHPQoox5ADvBIb9OZcicMdSwmd5PvsTQ"

# 테마 키워드 사전
THEME_KEYWORDS = {
    "자연":          ["산","계곡","공원","숲","호수","폭포","해변","휴양림","생태","자연"],
    "역사·문화":     ["사","사원","유적","유적지","고분","왕릉","고택","박물관","향교","서원"],
    "휴식·뷰 포인트":["전망대","카페","휴양","힐링","숲길","정원","쉼터","미술","전시","도서"],
    "체험·액티비티": ["체험","테마파크","놀이","모험","수영장","리조트","스파","아트"],
    "힐링":[]
    # "자연", "휴식·뷰 포인트",  "역사·문화", "힐링","체험·액티비티", "기타"
    # 각 테마 선정 이유 : 
    # 자연 : 산과 자연을 통틀어 
    # 휴식 뷰 포인트 : 야경, 산책이 가능하며 
    # 역사 문화 : 당연히 있어야 하는 분야
    # 힐링 : 바닷가나 해수욕장같이 움직임이 크게 없는 장소이자 장소 자체가 사람에게 좋은 기운을 주는 장소(사용자의 기분이 안좋으면 그걸 반영하여 올려주기 위한 장치)
    # 체험 액티비티 : 체험, 놀이공원 같은 활동 여행지
    # 기타 : 위에 해당되지 않는 여행지
}

def classify_theme(name: str) -> str:
    for theme, kws in THEME_KEYWORDS.items():
        if any(kw in name for kw in kws):
            return theme
    return "기타"

def get_google_rating(place_name: str) -> float:
    """
    최신 Places API Find Place From Text 사용
    - legacy API 에러 (REQUEST_DENIED) 방지를 위해
      Cloud Console에서 Places API 활성화 필수
    """
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input":       f"{place_name} 대한민국",
        "inputtype":   "textquery",
        "fields":      "rating",
        "key":         GOOGLE_API_KEY,
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        if data.get("status") != "OK":
            # 실패했으면 0.0 리턴
            return 0.0
        candidates = data.get("candidates", [])
        if not candidates:
            return 0.0
        return float(candidates[0].get("rating", 0.0))
    except Exception:
        # 네트워크나 JSON 파싱 에러 등 모두 0.0 처리
        return 0.0

def main():
    # 1) 엑셀 로드
    df = pd.read_excel(INPUT_FILE, engine="openpyxl")
    print("컬럼명 확인:", df.columns.tolist())

    # 2) 테마 분류
    df['테마'] = df['명칭'].astype(str).apply(classify_theme)

    # 3) 평점 조회 + 진행률 출력
    total = len(df)
    ratings = []
    for idx, name in enumerate(df['명칭'].astype(str), start=1):
        rt = get_google_rating(name)
        ratings.append(round(rt, 1))
        print(f"→ {idx}/{total} '{name}' 조회 완료 (평점: {round(rt,1)})")
        time.sleep(0.1)  # API 과다 호출 방지

    df['평점'] = ratings

    # 4) 결과 저장
    df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
    print(f"끝! 결과를 '{OUTPUT_FILE}' 에 저장했습니다.")

if __name__ == "__main__":
    main()
    
    
    