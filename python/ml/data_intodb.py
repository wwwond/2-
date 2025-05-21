import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.types import Integer, VARCHAR, DECIMAL, CLOB
from pathlib import Path

# 세팅팅 
BASE_DIR   = Path(__file__).resolve().parent
INPUT_XLSX = BASE_DIR / "tourlist_prep.xlsx"

user     = "GD"
password = "gdgd"
host     = "210.119.12.114"
port     = 1521
service  = "xe"

# 1) 엑셀 호출
df = pd.read_excel(INPUT_XLSX, engine="openpyxl")

# 2) 컬럼명 빈칸 제거 → 영어 매핑 
df.columns = df.columns.str.strip()

col_map = {
    "순번":          "placeId",
    "명칭":          "name",
    "테마":          "theme",
    "평점":          "avgRating",
    "주소":          "address",
    "위도":          "latitude",
    "경도":          "longitude",
    "개요":          "description",
    "유산구분":      "heritageType",
    "문의 및 안내":  "infoCenter",
    "쉬는날":        "closedDay",
    "체험안내":      "experienceInfo",
    "체험가능연령":   "minAge",
    "운영시간":      "businessHours",
    "주차시설":      "parkingInfo",
    "상세정보":      "details",
    "이미지" :       "image",
}

df.rename(columns=col_map, inplace=True)

# 3) 타입 매핑 
dtype_map = {
    "placeId":       Integer(),
    "name":           VARCHAR(100),
    "theme":          VARCHAR(80),
    "avgRating":     DECIMAL(3,2),
    "address":        VARCHAR(200),
    "latitude":       DECIMAL(9,6),
    "longitude":      DECIMAL(9,6),
    "description":    CLOB(),
    "heritageType":  VARCHAR(50),
    "infoCenter":    VARCHAR(2000),
    "closedDay":     VARCHAR(2000),
    "experienceInfo":CLOB(),
    "minAge":        VARCHAR(2000),
    "businessHours": VARCHAR(2000),
    "parkingInfo":   VARCHAR(2000),
    "details":        CLOB(),
    "image": VARCHAR(2000),
}

# 4) DB 연결 엔진
engine = create_engine(
    f"oracle+oracledb://{user}:{password}@{host}:{port}/?service_name={service}"
)
inspector = inspect(engine)
print("SQLAlchemy 가 보는 테이블 목록:", inspector.get_table_names())

# 5) 데이터 삽입
df.to_sql(
    name="place",
    con=engine,
    if_exists="replace",  
    index=False,
    dtype=dtype_map,
    chunksize=1           
)

# 확인영 
with engine.connect() as conn:
    total_db = conn.execute(text("SELECT COUNT(*) FROM PLACE")).scalar()
print(f"✔ DB에 총 {total_db}행 저장되었습니다 (엑셀 {len(df)}행).")