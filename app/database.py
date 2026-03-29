import os
import urllib.parse
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

def get_env_path():
    curr = Path(__file__).resolve()
    # .env 파일 찾아 올라가기 / 최대5회
    for _ in range(5):
        if (curr / '.env').exists():
            return curr / '.env'
        curr = curr.parent
    return None

env_path = get_env_path()
if env_path:
    load_dotenv(dotenv_path=env_path)

# DB설정 정보
DB_HOST = os.getenv("SUPABASE_HOST")
DB_PASSWORD = os.getenv("SUPABASE_PASSWORD")
DB_NAME = os.getenv("SUPABASE_NAME")
DB_USER = os.getenv("SUPABASE_USER")
DB_PORT = os.getenv("SUPABASE_USER", "5432") # 환경변수에 없으면 5432 사용

# 비밀번호 파싱, URL 생성
PW_PARSED = urllib.parse.quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
DB_URL = f"postgresql://{DB_USER}:{PW_PARSED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DB_URL)

# 1. 쿼리 실행 함수 (작성하신 코드 그대로!)
def get_data(query, engine):
    try:
        df = pd.read_sql(query, engine)
        print("데이터 로드 완료!")
        return df
    except Exception as e:
        print(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

# 2. 통합 쿼리 작성
query = """
SELECT
    i.id AS product_id,
    i.product_name,
    i.product_type,
    i.category,
    f.maturity,

    -- 🚨 여기를 다시 interest_rate로 원상복구!
    f.interest_rate,

    v.risk_level,
    v.eligible_tdf,
    v.launch_date,
    v.total_net_worth,
    v.total_expense_ratio,

    -- (얘네는 파이썬에서 return_1y를 찾으니 그대로 둡니다)
    v.average_return_1y AS return_1y,
    v.average_return_3y AS return_3y,
    v.average_return_5y AS return_5y

FROM product_info i
LEFT JOIN product_fixed f ON i.id = f.id
LEFT JOIN product_variable v ON i.id = v.id
"""

# 1. DB에서 데이터 가져오기
merged_df = get_data(query, engine)

# 2. 계산에 쓰이는 기둥들을 진짜 '숫자(Float)'로 강제 변환! ⭐
# errors='coerce'를 넣으면, 숫자로 바꿀 수 없는 이상한 글자가 있어도 에러를 내는 대신 빈칸(NaN)으로 안전하게 바꿔줍니다.
numeric_columns = [
    'interest_rate',
    'return_1y',
    'return_3y',
    'return_5y',
    'total_expense_ratio',
    'total_net_worth',
    'maturity'
]

for col in numeric_columns:
    if col in merged_df.columns:
        merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')

# 3. 문자를 숫자로 다 바꾼 후에, 빈칸(NaN)을 0으로 채워줍니다.
merged_df = merged_df.fillna(0)

# ==========================================
# (이하 기존 코드와 동일) 보장/비보장 쪼개기
# ==========================================
grnt_df = merged_df[merged_df['category'] == 'GUARANTEED'].copy()
notgrnt_df = merged_df[merged_df['category'] == 'NON_GUARANTEED'].copy()
