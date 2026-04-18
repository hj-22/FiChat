import streamlit as st
import difflib
from config import SURVEY_CONTENT, SURVEY_STEPS


def operator_match(user, operator, all_operators):
    if not operator.strip():
        st.warning("값을 입력해주세요")
        return
    
    # 1. 정확 매칭
    if operator in all_operators:
        user["pension_operator"] = operator
        st.rerun()

    # 유사도 검색
    matches = difflib.get_close_matches(
                    operator,
                    all_operators,
                    n=3,
                    cutoff=0.5   # 유사도 기준 (0~1)
                )

    if matches:
        st.warning("정확한 사업자가 없습니다. 혹시 아래 중 하나인가요?")
        for m in matches:
            if st.button(f"👉 {m}"):
                user["pension_operator"] = m
                st.rerun()

    else:
        st.error("유사한 사업자를 찾을 수 없습니다. 다시 입력해주세요.")



def show_survey_flow(all_operators):

    user = st.session_state.user

    st.header("투자 성향 진단")
    st.write("안녕하세요!")
    st.write("시작 전, 맞춤형 가이드를 위해 아래 설문을 작성해주세요 :waving hand:")



    for i, step in enumerate(SURVEY_STEPS):
        key = step["key"]
        label = step["label"]
        widget_type = step["type"]

        # 마지막 단계인지 확인
        # 먼저 유저에 입력이 되지 않은 질문 순서에서
        if user[key] is None:
            is_last_step = (i == len(SURVEY_STEPS) - 1)
            btn_label = "완료" if is_last_step else "다음"
            
        # label이 None이면 SURVEY_CONTENT에서 가져옴
        display_label = label if label else SURVEY_CONTENT[key]["label"]

        # 위젯별로 렌더링
        if widget_type == "number":
            val = st.number_input(display_label, min_value=0, step=1)
            if st.button(btn_label):
                # investment_amount는 만 단위 보정
                user[key] = val * 10000 if key == "investment_amount" else val
                st.rerun()

        elif widget_type == "radio":
            options = SURVEY_CONTENT[key]["options"]
            choice = st.radio(display_label, options)

            if st.button(btn_label):

                if key == "direct_manage":
                    user[key] = choice.startswith("1")  # 1로 시작하면 True
                else:
                    user[key] = int(choice[0])

                st.rerun()
        
        elif widget_type == "text_match":
            operator = st.text_input(display_label)
            if st.button(btn_label):
                operator_match(user, operator, all_operators)

        # 한 질문 끝나면 루프 중단 (enumerate for 루프)
        return True
    
    return False

        

