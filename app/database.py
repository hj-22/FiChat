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

def get_engine():
    return create_engine(DB_URL)

# 데이터 로드 함수: 엔진을 내부 호출로 변경. 쿼리만 넣어도 작동 가능
def get_data(query):
    engine = get_engine()
    try:
        # 커넥션을 명시적으로 열고 닫는 것이 권장된다고 함.(with 구문)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            print("데이터 로드 완료!")
            return df
    except Exception as e:
        print(f"데이터 로드 실패: {e}")
        return pd.DataFrame()
