import streamlit as st
from chatbot import chatbot, generate_questions


def show_chatbot_interface(vectorstore, grnt_df, notgrnt_df):

    # 아직 추천 결과가 없는 경우 -> 추천 버튼 보여주기
    if "recs" not in st.session_state:

        if st.button("추천 받기"):
            # 챗봇 로직 호출, response, user, portfolio
            response, user, recs = chatbot(
                "추천해주세요",
                st.session_state.user,
                "session1",
                vectorstore,
                grnt_df,
                notgrnt_df
            )

            # 세션에 결과 저장
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

    # ==============================
    # 추천 결과가 있음 -> 채팅 모드
    # ==============================
    else:
        st.subheader("💬 챗봇과 대화하기")

        # 👉 기존 대화 출력 (중요)
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
                vectorstore,
                grnt_df,
                notgrnt_df
            )

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