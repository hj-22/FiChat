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


    # ---------------- 설문 UI 출력 ----------------
    is_surveying = show_survey_flow(all_operators)




    user_profile = build_user_profile(inputs)
    grnt_df, notgrnt_df = get_categorized_products(user_profile)

    recommendations = get_portfolio_recommendation(user_profile, grnt_df, notgrnt_df)




    # 다 입력되면 chatbot 호출
    # 추천 완료 이후
    else:
        st.success("모든 정보 입력 완료!")
        user["risk_preference"] = risk_preference_question(user)

        # 1️⃣ 최초 추천 버튼
        if "recs" not in st.session_state:
            if st.button("추천 받기"):
                response, user, recs = chatbot(
                    "추천해주세요",
                    st.session_state.user,
                    "session1",
                    vectorstore
                )

                st.session_state.user = user
                st.session_state.recs = recs

                st.session_state.messages = [{
                    "role": "assistant",
                    "content": response
                }]

                st.rerun()

        # ==============================
        # 💬 추천 완료 이후 챗봇 영역
        # ==============================

        else:
            st.success("모든 정보 입력 완료!")

            # ------------------------------
            # 1️⃣ 최초 추천
            # ------------------------------
            if "recs" not in st.session_state:

                if st.button("추천 받기"):

                    response, user, recs = chatbot(
                        "추천해주세요",
                        st.session_state.user,
                        "session1",
                        vectorstore
                    )

                    st.session_state.user = user
                    st.session_state.recs = recs

                    # 메시지 초기화
                    st.session_state.messages = [{
                        "role": "assistant",
                        "content": response
                    }]

                    # 추천 질문 초기화
                    if "suggested_questions" in st.session_state:
                        del st.session_state["suggested_questions"]

                    st.rerun()

            # ------------------------------
            # 2️⃣ 채팅 모드
            # ------------------------------
            else:
                st.subheader("💬 챗봇과 대화하기")

                # 👉 기존 대화 출력 (중요)
                if "messages" in st.session_state:
                    for msg in st.session_state.messages:
                        with st.chat_message(msg["role"]):
                            st.write(msg["content"])

                # 👉 사용자 입력
                user_input = st.chat_input("궁금한 점을 물어보세요")

                if user_input:

                    # user 메시지 저장
                    st.session_state.messages.append({
                        "role": "user",
                        "content": user_input
                    })

                    # 챗봇 실행
                    response, user, recs = chatbot(
                        user_input,
                        st.session_state.user,
                        "session1",
                        vectorstore
                    )

                    st.session_state.user = user
                    st.session_state.recs = recs

                    # assistant 메시지 저장
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

                    # 추천 질문 초기화 (새 질문 기준으로 다시 생성)
                    if "suggested_questions" in st.session_state:
                        del st.session_state["suggested_questions"]

                    st.rerun()


        # ==============================
        # 💡 추천 질문 영역
        # ==============================

        # 👉 추천 질문 생성 (RAG 기반)
        if "recs" in st.session_state and "suggested_questions" not in st.session_state:

            st.session_state.suggested_questions = generate_questions(
                st.session_state.user,
                st.session_state.recs,
                vectorstore   # 🔥 중요
            )


        # 👉 추천 질문 UI
        if "suggested_questions" in st.session_state:

            st.subheader("💡 추천 질문")

            cols = st.columns(3)

            for i, q in enumerate(st.session_state.suggested_questions):

                if cols[i].button(q):

                    # user 메시지 추가
                    st.session_state.messages.append({
                        "role": "user",
                        "content": q
                    })

                    # 챗봇 실행
                    response, user, recs = chatbot(
                        q,
                        st.session_state.user,
                        "session1",
                        vectorstore
                    )

                    st.session_state.user = user
                    st.session_state.recs = recs

                    # 추천 질문 초기화
                    if "suggested_questions" in st.session_state:
                        del st.session_state["suggested_questions"]

                    # assistant 메시지 추가
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

                    st.rerun()