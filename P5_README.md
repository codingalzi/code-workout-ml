# P5 Lab — 서울 따릉이 이용 패턴과 K-means

**학생용** `p5_project_seoul_bike_clustering.ipynb` + `p5_demo_station_profiles_2025.csv`를 같은 폴더에 놓고 위에서부터 실행합니다.

- 모의 데이터는 **실제 서울시 데이터가 아닙니다**. 실제 분석은 공식 자료를 가공한 `p5_station_profiles_2025.csv`로 진행합니다. 노트북에서 `DATA_FILE`만 변경하세요.
- 한 행은 **대여소 한 곳**입니다. `m01`~`m12`는 월별 대여건수, `wd_h00`~`wd_h23`은 평일 시간대별 일평균 대여건수, `we_h00`~`we_h23`은 주말 시간대별 일평균 대여건수입니다.
- `wd`는 월~금, `we`는 토~일입니다. 공휴일은 별도로 구분하지 않습니다.
- 노트북에서 필요한 패키지: `pandas`, `matplotlib`, `scikit-learn`.

**교수자용** `p5_prepare_seoul_bike.py`는 서울 열린데이터광장에서 확보한 2025년 시간대별 CSV 원자료를 학생용 1행/대여소 CSV로 집계하는 코드입니다. `raw_2025/`에 CSV를 넣고 `python p5_prepare_seoul_bike.py`를 실행합니다. 원자료 인코딩이나 열 이름이 다르면 코드 상단의 지정 값을 조정해야 합니다.

원자료: https://data.seoul.go.kr/dataList/OA-15245/F/1/datasetView.do

**검증:** 학생용 노트북은 동봉된 모의 데이터로 전체 셀 실행을 점검했습니다. 실제 서울시 공식 파일 전체를 다운로드해 실행 검증한 것은 아닙니다. 공식 자료 제출 전에는 연도·12개월 범위·이상 결측·대여소 운영 여부를 교수자가 확인해야 합니다.
