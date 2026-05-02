import streamlit as st
from chatbot import chatbot, generate_questions


def show_chatbot_interface(vectorstore, grnt_df, notgrnt_df):

    # 채팅 로직 관리
    def handle_chat(user_input):
        # user 메시지 저장
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 챗봇 실행
        response, user, recs = chatbot(
            user_input,
            st.session_state.user,
            "session1",
            vectorstore,
            grnt_df,
            notgrnt_df
        )

        # 결과, assistant 메시지 저장
        st.session_state.recs = recs
        st.session_state.messages.append({"role": "assistant", "content": response})

        # 추천 질문 초기화 (새 질문 기준으로 다시 생성)
        # suggested_questions이 세션에 존재하면 pop, 아니면 None반환하고 넘어감
        st.session_state.pop("suggested_questions", None)
        st.rerun()



    # 아직 추천 결과가 없는 경우 -> 추천 버튼 보여주기
    if "recs" not in st.session_state:
        if st.button("추천 받기"):
            # 챗봇 로직 호출, response, user, portfolio
            # 최초 추천 -> input이 "추천해주세요" 
            response, user, recs = chatbot(
                "추천해주세요",
                st.session_state.user,
                "session1",
                vectorstore,
                grnt_df,
                notgrnt_df
            )
            st.session_state.recs = recs
            # messages 최초 정의 (이후 handle_chat을 통해 append됨.)
            st.session_state.messages = [{"role": "assistant", "content": response}]
            # 추천 질문 초기화
            st.session_state.pop("suggested_questions", None)
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
        # 입력이 있으면 대화 시작
        if user_input:
            handle_chat(user_input)


    # ==============================
    # 💡 추천 질문 영역
    # ==============================

    # 👉 추천 질문 생성 (RAG 기반)
    if "recs" in st.session_state:
        # 질문 생성 로직 호출
        if "suggested_questions" not in st.session_state:
            st.session_state.suggested_questions = generate_questions(
                st.session_state.user,
                st.session_state.recs,
                vectorstore   
            )

        # 👉 추천 질문 UI
        # suggested_questions은 recs가 있을 때만 생성됨
        if "suggested_questions" in st.session_state:
            st.write("---")
            st.caption("💡이런 질문은 어떠세요?")
            cols = st.columns(len(st.session_state.suggested_questions))
            for i, q in enumerate(st.session_state.suggested_questions):
                if cols[i].button(q, width="stretch"):
                    handle_chat(q)