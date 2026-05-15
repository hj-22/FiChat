from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from .llm_build import get_embedding_model, get_llm_model
from .prompt import get_chatbot_prompt, get_chat_chain

llm = get_llm_model()
prompt = get_chatbot_prompt()
chain = get_chat_chain(llm, prompt)


def generate_bot_response(portfolio, user_input):
    # 딕셔너리를 텍스트로 변환!
    context_text = build_portfolio_context(portfolio)

    system_prompt = f"""
    너는 고객의 퇴직연금을 관리해주는 AI 어드바이저야.
    아래 [추천 포트폴리오]는 백엔드 시스템이 철저한 계산을 통해 뽑아낸 결과야.
    이 데이터를 바탕으로 고객의 질문에 친절하고 전문적으로 답해줘.

    [추천 포트폴리오]
    {context_text}

    고객 질문: "{user_input}"
    """

    # 4. AI에게 프롬프트를 쏴주고(invoke) 결과 받기
    result = llm.invoke(system_prompt)

    # 지금은 테스트를 위해 프롬프트 자체를 출력해봅니다.
    return system_prompt



## 2단계: 딕셔너리를 텍스트로 변환 (build_portfolio_context)
# 1단계에서 만든 딕셔너리를 LLM이 읽을 수 있게 줄글로

def build_portfolio_context(portfolio):
    s = portfolio["summary"]

    context = f"[투자 요약]\n"
    context += f"- 투자성향: {s['risk_preference']}\n"
    context += f"- 총 투자금: {s['total_amt']:,}원\n"
    context += f"- 자산배분: 원리금보장형 {s['grnt_ratio']*100}% / 실적배당형 {s['ungrnt_ratio']*100}%\n\n"

    context += "[원리금 보장형 추천]\n"
    for i, p in enumerate(portfolio["guaranteed"]):
        reasons_text = ", ".join(p["reasons"])
        context += f"{i+1}위. {p['product_name']} (점수: {p['score']}점) - 특징: {reasons_text}\n"

    context += "\n[실적 배당형(비보장형) 추천]\n"
    for i, p in enumerate(portfolio["non_guaranteed"]):
        reasons_text = ", ".join(p["reasons"])
        context += f"{i+1}위. {p['product_name']} (점수: {p['score']}점) - 특징: {reasons_text}\n"

    return context



# 1. RAG용 문서 생성기 (build_documents)

def build_documents(merged_df):
    """DB에서 가져온 통합 데이터프레임을 LangChain RAG 문서로 변환합니다."""
    docs = []
    for _, row in merged_df.iterrows():
        # SQL에서 AS product_id 로 가져온 값을 사용합니다.
        product_id = row.get('product_id', '')
        product_name = row.get('product_name', '이름 없음')
        category = row.get('category', '')
        product_type = row.get('product_type', '')

        # 공통 정보 블록
        content = f"""[상품 기본 정보]
- 상품명: {product_name}
- 상품 유형: {product_type}
- 상품 구분: {'원리금 보장형' if category == 'GUARANTEED' else '실적 배당형(비보장형)'}
"""
        # 보장형 상세 정보
        if category == 'GUARANTEED':
            content += f"""
[수익 및 금리 안내]
- 만기: {row.get('maturity', 0)}개월
- 적용 이율(금리): {row.get('interest_rate', 0)}%
- 특징: 만기 시 원금과 약정된 이율을 보장하는 안전한 상품입니다.
"""
        # 비보장형 상세 정보
        elif category == 'NON_GUARANTEED':
            content += f"""
[상품 상세 스펙]
- 위험 등급: {row.get('risk_level', '정보 없음')}
- TDF 편입 여부: {'편입(O)' if row.get('eligible_tdf') == 'O' else '미편입(X)'}
- 상품 설정일: {row.get('launch_date', '정보 없음')}
- 순자산 규모: {row.get('total_net_worth', 0)}
- 총 보수(수수료율): {row.get('total_expense_ratio', 0)}%

[과거 평균 수익률 내역]
- 최근 1년 수익률: {row.get('return_1y', 0)}%
- 최근 3년 수익률: {row.get('return_3y', 0)}%
- 최근 5년 수익률: {row.get('return_5y', 0)}%
* 주의: 과거 수익률이 미래의 수익을 보장하지 않습니다.
"""
        # 메타데이터에 product_id를 필수로 넣습니다!
        docs.append(Document(
            page_content=content.strip(),
            metadata={"product_id": product_id, "category": category}
        ))
    return docs

# ==========================================
# 2. 벡터스토어 및 검색기 (Retriever) 설정
# ==========================================
def retrieve_with_filter(user_query, candidate_ids, vectorstore):
    """RAG 검색 시, 추천된 상품(candidate_ids) 안에서만 약관/상세정보를 찾도록 필터링합니다."""
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 3,
            # FAISS에서 메타데이터를 필터링하는 방식 (ID가 후보 리스트에 있는지 확인)
            "filter": lambda metadata: metadata.get("product_id") in candidate_ids
        }
    )
    return retriever.invoke(user_query)

# ==========================================
# 4. 최종 RAG 파이프라인 (rag_pipeline)
# ==========================================
def rag_pipeline(user_query, user, portfolio, vectorstore):

    # 🔥 0️⃣ 추천 요청인지 판단
    is_recommendation = user_query.strip() in ["추천", "추천해주세요", "상품 추천", "포트폴리오 추천"]

    # 🔥 1️⃣ 기본 portfolio context 생성
    portfolio_context = build_portfolio_context(portfolio)

    # 🔥 2️⃣ 추천 상품 리스트
    all_recs = portfolio["guaranteed"] + portfolio["non_guaranteed"]

    candidate_ids = [
        r["product_info"]["product_id"]
        for r in all_recs
    ]

    # 🔥 3️⃣ RAG 검색
    retrieved_docs = retrieve_with_filter(user_query, candidate_ids, vectorstore)
    rag_text = "\n\n".join([d.page_content for d in retrieved_docs])

    # 🔥 4️⃣ context 구성 (핵심 분기)
    if is_recommendation:
        # 👉 추천 요청이면 portfolio 중심
        final_context = f"""
        [추천 포트폴리오]
        {portfolio_context}

        [추가 정보]
        {rag_text}
        """
    else:
        # 👉 일반 질문이면 이유 + rag 중심
        reason_text = "[시스템 추천 사유]\n"
        for r in all_recs:
            p_name = r["product_name"]
            reasons = "\n  - ".join(r["reasons"])
            reason_text += f"■ {p_name} (추천 점수: {r['score']}점)\n  - {reasons}\n\n"

        final_context = f"""
        {portfolio_context}

        {reason_text}

        [검색된 상세 정보]
        {rag_text}
        """

    # 🔥 5️⃣ LLM 호출
    result = chain.invoke({
        "context": final_context,
        "user": user,
        "user_query": user_query
    })

    return result.content



def generate_questions(user, recs, vectorstore):

    # 🔥 1️⃣ 리스트 합치기
    all_recs = recs["guaranteed"] + recs["non_guaranteed"]

    # 🔥 2️⃣ candidate_ids
    candidate_ids = [
        r["product_info"]["product_id"]
        for r in all_recs
    ]

    # 🔥 3️⃣ RAG 검색
    rag_docs = retrieve_with_filter(
        "이 상품들의 특징과 차이",
        candidate_ids,
        vectorstore
    )

    rag_text = "\n".join([d.page_content for d in rag_docs])

    # 🔥 4️⃣ 상품 이름
    product_text = "\n".join([
        r["product_name"] for r in all_recs
    ])

    # 🔥 5️⃣ LLM
    res = llm.invoke(f"""
    사용자 정보:
    {user}

    추천 상품:
    {product_text}

    상품 상세 정보:
    {rag_text}

    위 정보를 기반으로
    사용자가 다음으로 물어볼 만한 질문 3개를 생성하세요.

    조건:
    - 반드시 질문 문장만 출력
    - 설명 금지
    - 번호 금지
    - 중복 금지
    - 구체적인 질문
    - 무조건 한국어
    - 한국어와 필요시 영어 사용을 제외한 다른 언어는 잘못된 출력값임
    """).content

    return [q.strip() for q in res.split("\n") if len(q) > 5][:3]


# 2. 문서 만들기 (이전에 만드신 merged_df 사용)
def build_vectorstore(merged_df):
    """
    사용자의 추천 상품 리스트(merged_df)를 바탕으로 
    메모리 상에 실시간 Vector DB를 구축합니다.
    """
    docs = build_documents(merged_df)

    # 임베딩 모델 로드(캐시된 것 가져오기)
    embedding = get_embedding_model()

    # 3. Vector DB 생성 (메모리 상에 생성됨)
    vectorstore = FAISS.from_documents(docs, embedding)
    
    return vectorstore








