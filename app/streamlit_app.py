# 흐름: db에서 가입 사업자 기준으로 먼저 필터링해서 가져오기
# 이후 가져온 데이터로 계산

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# --- 1. 페이지 설정 ---
# set_page_config는 반드시 가장 먼저 실행되어야 함.
st.set_page_config(page_title="FiChat", page_icon=":chart_with_upwards_trend:")

# --- 2. 커스텀 모듈 import ---
from database import get_env_path, get_data
from models import SurveyAnswers
from user_profile import build_user_profile, risk_preference_question
from recommender import get_categorized_products
from survey_UI import show_survey_flow
from app_ui import show_chatbot_interface
from chatbot.rag import build_vectorstore

# --- 3. 환경변수 설정 및 세션 초기화 영역 ------
env_path = get_env_path()
if env_path:
    load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")

if "user" not in st.session_state:
    st.session_state.user = {
        "age": None, "period": None, "experience": None,
        "psychology": None, "loss_level": None, "finance_knowledge": None,
        "investment_goal": None, "pension_ratio": None, "expected_income": None,
        "risk_preference": None, "investment_amount": None,
        "pension_operator": None, "direct_manage": None
    }

# 채팅 내역도 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 설문 플래그
if "survey_done" not in st.session_state:
    st.session_state.survey_done = False

# -------------------------------------------------------
# --- 4. main 로직 함수 ---
def main():
    st.title("💬 노후 대비 금융 상품 추천 챗봇")

    # 사업자 리스트 가져오기
    try:
        # get_data가 데이터프레임 형태로 반환 -> 매칭을 위해 리스트 형태로 가공 필요
        all_operators = get_data(query="SELECT operator_name FROM operator_info")["operator_name"].tolist()
    except Exception as e:
        # 로그만 남기고 프로그램은 계속 진행
        st.error("사업자 정보를 불러오는 중 문제가 발생했습니다.")
        # print(f"DB Error: {e}")
        # DB연결 실패시에도 오류 없게 빈 리스트
        all_operators = []

    # ================ UI구성 ================ #

    ## 화면 나누기
    if not st.session_state.survey_done:
        # --- 설문 모드 ---
        is_surveying = show_survey_flow(all_operators)
        if not is_surveying:
            st.session_state.survey_done = True
            st.rerun()

    else:
        # --- 챗봇 모드 (설문 완료 후 진입) ---
        # 기본 정보 가공
        if "vectorstore" not in st.session_state:
            with st.spinner("사용자 투자 성향 및 맞춤 상품 분석 중...", show_time=True):
                # 데이터 가공
                user = st.session_state.user
                user_profile = build_user_profile(user)
                grnt_df, notgrnt_df = get_categorized_products(user_profile)
                
                # 투자 성향 확정
                if user.get("risk_preference") is None:
                    user["risk_preference"] = risk_preference_question(user)
                
                # Vectorstore 생성
                merged_df = pd.concat([grnt_df, notgrnt_df])
                st.session_state.vectorstore = build_vectorstore(merged_df)
                
                # 상품 데이터도 세션에 저장 (chatbot_interface에서 쓰기 위함)
                st.session_state.grnt_df = grnt_df
                st.session_state.notgrnt_df = notgrnt_df
            
            st.success("모든 분석이 완료되었습니다!")
            st.rerun()

        # 최종 인터페이스 호출
        show_chatbot_interface(
            st.session_state.vectorstore, 
            st.session_state.grnt_df, 
            st.session_state.notgrnt_df
        )


if __name__ == "__main__":
    main()