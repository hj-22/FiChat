from langchain_core.prompts import ChatPromptTemplate

def get_chatbot_prompt():
    """프롬프트 템플릿"""

    return ChatPromptTemplate.from_messages([
        ("system", """
        너는 전문적이고 친절한 퇴직연금 AI 어드바이저다.

        다음 규칙을 반드시 지켜라:
        1. 상품명(예: TDF, ETF 등)이나 필수 금융 용어를 제외하고는 100% 자연스러운 한국어로 작성한다.
        2. 한글과 영어를 제외한 문자는 무조건 사용해서는 안 된다. 해당 규칙을 어길 경우 잘못된 대답이다.
        3. 고객에게 존댓말을 사용하며 신뢰감 있는 말투를 사용한다.
        4. 제공된 [시스템 추천 사유]와 [검색된 상세 정보]만을 바탕으로 답변한다.
        5. 고객의 질문에 직접적으로 답하면서, 왜 이 상품이 추천되었는지 명확히 설명한다.
        """),
            ("human", """
        [고객 정보]
        - 나이: {age}세
        - 투자 성향: {risk_preference}
        - 은퇴까지 남은 기간: {period}년

        [고객의 실제 질문]
        "{user_query}"

        [추천 데이터 및 상세 정보]
        {context}

        위 정보를 바탕으로 고객의 질문에 완벽하게 답변해 주세요.
        """)
        ])


def get_chat_chain(llm, prompt):
    """체인 구성"""
    # 딕셔너리 키값은 build_user_profile() 에서 만든 키값과 동일하게 맞췄습니다.
    chain = (
        {
            "context": lambda x: x["context"],
            "age": lambda x: x["user"]["age"],
            "risk_preference": lambda x: x["user"]["risk_preference"],
            "period": lambda x: x["user"]["period"],
            "user_query": lambda x: x["user_query"]
        }
        | prompt
        | llm
    )
    return chain

