"""교수자용: 서울시 2025년 '대여이력' CSV → P5 대여소별 집계 CSV.

1. 2025년 대여이력 ZIP을 내려받아 raw_2025/에 압축 해제합니다.
2. python p5_prepare_seoul_bike_v2.py 를 실행합니다.
원본 파일 형식에 따라 ENCODING 또는 한글 열 이름을 조정할 수 있습니다.
"""
from collections import Counter
from pathlib import Path
import pandas as pd

YEAR = 2025
ENCODING = "cp949"
RAW = Path("raw_2025")
MIN_RENTALS = 1000  # 지나치게 적게 이용된 대여소 제외

hours = Counter()
months = Counter()
names = {}
needed = {"대여일시", "대여대여소번호", "대여대여소명",
          "반납일시", "반납대여소번호", "반납대여소명"}

# 원본이 크므로 20만 건씩 읽고 필요한 건수만 누적합니다.
for file in sorted(RAW.rglob("*.csv")):
    print("읽는 중:", file.name)
    for chunk in pd.read_csv(file, encoding=ENCODING, dtype=str,
                             usecols=lambda c: c.strip().replace(" ", "") in needed,
                             chunksize=200_000):
        chunk.columns = [c.strip().replace(" ", "") for c in chunk.columns]

        for kind, date_col, id_col, name_col in [
            ("r", "대여일시", "대여대여소번호", "대여대여소명"),
            ("b", "반납일시", "반납대여소번호", "반납대여소명")
        ]:
            dt = pd.to_datetime(chunk[date_col], errors="coerce")
            part = pd.DataFrame({
                "station": chunk[id_col],
                "name": chunk[name_col],
                "month": dt.dt.month,
                "day": dt.dt.weekday.map(lambda x: "wd" if x < 5 else "we"),
                "hour": dt.dt.hour,
            })
            part = part[dt.dt.year.eq(YEAR) & part["station"].notna()]
            groups = part.groupby(["station", "day", "hour"]).size()
            hours.update({(kind, s, d, int(h)): int(n)
                          for (s, d, h), n in groups.items()})
            if kind == "r":
                months.update(part.groupby(["station", "month"]).size().to_dict())
            names.update(part.groupby("station")["name"].last().to_dict())

stations = sorted({s for (_, s, _, _) in hours})
rows = []
for s in stations:
    r = sum(hours["r", s, d, h] for d in ("wd", "we") for h in range(24))
    b = sum(hours["b", s, d, h] for d in ("wd", "we") for h in range(24))
    # 12개월 모두 대여기록이 있으며 이용량이 충분한 대여소만 분석합니다.
    if min(r, b) < MIN_RENTALS or any(months[s, m] == 0 for m in range(1, 13)):
        continue
    row = {"station_id": s, "station_name": names.get(s, s),
           "annual_rentals": r, "annual_returns": b}
    row.update({f"m{m:02}": months[s, m] for m in range(1, 13)})
    row.update({f"{kind}_{d}_h{h:02}": hours[kind, s, d, h]
                for kind in ("r", "b") for d in ("wd", "we") for h in range(24)})
    rows.append(row)

if not rows:
    raise ValueError("분석할 대여소가 없습니다. 원본과 연도·대여소 기준을 확인하세요.")
output = f"p5_station_profiles_{YEAR}.csv"
pd.DataFrame(rows).to_csv(output, index=False, encoding="utf-8-sig")
print(f"저장: {output} / {len(rows)}개 대여소")
