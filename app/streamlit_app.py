# 흐름: db에서 가입 사업자 기준으로 먼저 필터링해서 가져오기
# 이후 가져온 데이터로 계산
from models import SurveyAnswers
from user_profile import build_user_profile, risk_preference_question
from recommender import get_categorized_products, get_portfolio_recommendation
from survey_UI import show_survey_flow

import os
import difflib
from database import get_env_path, get_data


from dotenv import load_dotenv

env_path = get_env_path()
if env_path:
    load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")


import streamlit as st


# 초기화
# 초기화 코드는 파일의 가장 최상단에 두어야 한다
if "user" not in st.session_state:
    st.session_state.user = {
        "age": None,
        "period": None,
        "experience": None,
        "psychology": None,
        "loss_tolerance": None,
        "knowledge": None,
        "goal": None,
        "pension_ratio": None,
        "income_future": None,
        "risk_preference": None,
        "investment_amount": None,
        "pension_operator": None,
        "direct_manage": None
    }
user = st.session_state.user

# 채팅 내역도 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []


def main():

    # Streamlit UI
    st.set_page_config(page_title="FiChat", page_icon=":chart_with_upwards_trend:")
    st.title("💬 노후 대비 금융 상품 추천 챗봇")


    # --- 테스트용 버튼 (개발 중에만 사용) ---
    if st.sidebar.button("🧪 예시 데이터 채우기"):
        st.session_state.user = {
            "age": 30, "period": 10, "experience": 3, "psychology": 2,
            "loss_tolerance": 1, "knowledge": 2, "goal": 3, "pension_ratio": 1,
            "income_future": 4, "investment_amount": 5000000,
            "pension_operator": "미래에셋증권", "direct_manage": True
        }
        st.rerun()

    # 사업자 리스트 가져오기
    # 초기화, DB연결 실패시에도 오류 없게
    all_operators = []
    try:
        all_operators = get_data(query="SELECT operator_name FROM operator_info")
    except Exception as e:
        # 로그만 남기고 프로그램은 계속 진행
        st.error("사업자 정보를 불러오는 중 문제가 발생했습니다.")
        print(f"DB Error: {e}")


    # ================ UI구성 ================ #
    # 설문 플래그
    if "survey_done" not in st.session_state:
        st.session_state.survey_done = False

    ## 화면 나누기

    if not st.session_state.survey_done:
        # --- 설문 모드 ---
        is_surveying = show_survey_flow(all_operators)

        if not is_surveying:
            st.session_state.survey_done = True
            st.rerun()

    else:
        # --- 챗봇 모드 ---
        if "risk_preference" not in user or user["risk_preference"] is None:
            st.success("모든 정보 입력 완료!")
            # 투자 성향 확정
            user["risk_preference"] = risk_preference_question(user)

        # 챗봇 인터페이스 




    user_profile = build_user_profile(inputs)
    grnt_df, notgrnt_df = get_categorized_products(user_profile)

    recommendations = get_portfolio_recommendation(user_profile, grnt_df, notgrnt_df)



