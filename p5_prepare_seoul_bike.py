"""교수자용: 서울 따릉이 시간대별 원자료(CSV) → 학생용 대여소별 데이터.

2025년 월별 CSV를 raw_2025/ 폴더에 넣고 실행하세요.
원자료 인코딩/열 이름이 다르면 아래 설정을 바꾸면 됩니다.
"""
from collections import defaultdict
from pathlib import Path
import pandas as pd
import numpy as np

YEAR = 2025
ENCODING = "cp949"
RAW_FOLDER = Path("raw_2025")
OUTPUT = f"p5_station_profiles_{YEAR}.csv"

# 공식 파일의 한글 열 이름과 API 열 이름을 공통 이름으로 통일한다.
RENAME = {
    "대여일시": "date", "RENT_DT": "date",
    "대여시간": "hour", "RENT_HR": "hour",
    "대여소번호": "station_id", "RENT_ID": "station_id",
    "대여소명": "station_name", "RENT_NM": "station_name",
    "이용건수": "count", "USE_CNT": "count",
}

hourly = defaultdict(float)
monthly = defaultdict(float)
station_names = {}

# 큰 원본을 조금씩 읽어 월·요일·시간별 건수를 합한다.
for file in sorted(RAW_FOLDER.glob("*.csv")):
    print("읽기:", file.name)
    for chunk in pd.read_csv(file, encoding=ENCODING, chunksize=200_000):
        chunk = chunk.rename(columns=RENAME)
        date = pd.to_datetime(
            chunk["date"].astype(str).str.replace(".", "-", regex=False),
            format="mixed", errors="coerce"
        )
        part = pd.DataFrame({
            "station_id": chunk["station_id"].astype(str),
            "month": date.dt.month,
            "day_type": np.where(date.dt.weekday < 5, "wd", "we"),
            "hour": pd.to_numeric(chunk["hour"], errors="coerce"),
            "count": pd.to_numeric(chunk["count"], errors="coerce"),
        })
        part = part[date.dt.year.eq(YEAR) & part["hour"].between(0, 23)]
        for key, value in part.groupby(["station_id", "month"])["count"].sum().items():
            monthly[key] += value
        for key, value in part.groupby(["station_id", "day_type", "hour"])["count"].sum().items():
            hourly[key] += value
        if "station_name" in chunk:
            station_names.update(dict(zip(chunk["station_id"].astype(str), chunk["station_name"])))

# 달마다 일수가 달라도 연간 일평균이 정확하도록 2025년의 요일별 일수로 나눈다.
calendar = pd.date_range(f"{YEAR}-01-01", f"{YEAR}-12-31")
days = {"wd": sum(calendar.weekday < 5), "we": sum(calendar.weekday >= 5)}
stations = sorted({station for station, month in monthly})
rows = []
for station in stations:
    if sum((station, m) in monthly for m in range(1, 13)) != 12:
        continue  # 12개월 기록이 모두 있는 대여소만 사용
    row = {"station_id": station,
           "station_name": station_names.get(station, station),
           "annual_rentals": sum(monthly[station, m] for m in range(1, 13))}
    row.update({f"m{m:02}": monthly[station, m] for m in range(1, 13)})
    row.update({f"{d}_h{h:02}": hourly[station, d, h] / days[d]
                for d in ["wd", "we"] for h in range(24)})
    rows.append(row)

pd.DataFrame(rows).to_csv(OUTPUT, index=False, encoding="utf-8-sig")
print(f"저장: {OUTPUT} ({len(rows)}개 대여소)")
