'''
실행 전 엑셀 파일명이 data.xlsx인지 확인해 주세요!!!
'''


import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


# 환경변수
DB_USER = "root"
DB_PW = os.getenv("DB_ROOT_PASSWORD")   # yml 에서 ${DB_ROOT_PASSWORD}
DB_HOST = "localhost"
DB_PORT = "3307"
DB_NAME = "pension_db"

# 연결 URL
'''
mysql+pymysql://root:password@localhost:3307/pension_db
mysql+pymysql : mysql데이터베이스에 접속, pymysql라이브러리를 엔진으로 사용
root(접속계정), localhost(내컴퓨터), 3307(포트번호)
'''
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)


def upload_excel_to_db(file_path):

    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        print(f"파일 이름이 data.xlsx인지 확인해 주세요.")
        return

    try:
        excel_data = pd.ExcelFile(file_path)
        print(f"파일 여는 중..")

        for sheet_name in excel_data.sheet_names:
            if sheet_name.startswith("product_"):
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # con: connection, pandas가 데이터를 어디로 보낼지 지정하는 매개변수
                # df라는 데이터를 engine을 타고 가서 sheet_name이라는 테이블에 입력하세요
                df.to_sql(name=sheet_name, con=engine, if_exists='replace', index=False)
        print("\n 데이터를 성공적으로 입력했습니다!")
    
    except Exception as e:
        print(f"\n 오류 발생: {e}")



if __name__ == "__main__":
    # 실행 전 엑셀 파일명을 확인하세요
    upload_excel_to_db("data.xlsx")