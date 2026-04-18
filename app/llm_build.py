from user_profile import asset_allocation
from recommender.engine import calculate_grnt_score, calculate_notgrnt_score, generate_reasons, generate_notgrnt_reasons


## 1단계 : 모든 로직을 묶어주는 래퍼(Wrapper) 함수 만들기
# 함수들을 실행해서 추천한 portfolio를 만들어서 하나의 딕셔너리로 깔끔하게 묶어주는 역할
def get_portfolio_recommendation(user_info, grnt_df, notgrnt_df, top_n=3):
    """
    고객의 자산 배분 비율을 계산하고, 스코어 기반으로 보장형/비보장형 상품을 각각 top_n개씩 추천해 주는 최종 통합 함수
    """

    # 1. 자산 배분 비율 및 유저 파라미터 추출

    risk_pref = user_info.get("risk_preference", "위험중립형")
    total_amt = user_info.get("investment_amount", 0)

    # 자산 배분 비율 (예: 원리금보장 60%, 비보장 40%)
    grnt_ratio = asset_allocation(risk_pref)
    ungrnt_ratio = 1.0 - grnt_ratio

    # 비보장형 계산을 위한 특수 파라미터 (실버 모드 및 직접 운용 여부)
    direct_manage = user_info.get("direct_manage", True)
    user_M = '내가 직접 알아보고 투자하고 싶다' if direct_manage else '전적으로 전문가에게 맡기고 싶다'

    period = user_info.get("period", 10)
    is_silver_mode = True if isinstance(period, (int, float)) and period <= 5 else False

    
    # 2. 보장형 상품 스코어링 및 Top N 추출
    scored_grnt = calculate_grnt_score(grnt_df.copy(), user_info)
    top_grnt = scored_grnt.sort_values(by="score", ascending=False).head(top_n)

    grnt_results = []
    for _, row in top_grnt.iterrows():
        # generate_reasons 파라미터에 scored_grnt 데이터프레임 전달
        reasons = generate_reasons(row, user_info, scored_grnt)
        grnt_results.append({
            "product_name": row["product_name"],
            "score": round(row["score"], 1),
            "reasons": reasons,
            "product_info": row.to_dict() # 챗봇 RAG나 화면에 뿌려줄 때 쓸 전체 정보
        })


    # 3. 비보장형 상품 스코어링 및 Top N 추출
    scored_notgrnt = calculate_notgrnt_score(notgrnt_df.copy(), user_M, risk_pref, is_silver_mode)
    top_notgrnt = scored_notgrnt.head(top_n)

    notgrnt_results = []
    for _, row in top_notgrnt.iterrows():
        reasons = generate_notgrnt_reasons(row, user_info)
        notgrnt_results.append({
            "product_name": row["product_name"],
            "score": round(row["Total_Score"], 1),
            "reasons": reasons,
            "product_info": row.to_dict() # 챗봇 RAG나 화면에 뿌려줄 때 쓸 전체 정보
        })

    # ==========================================
    # 4. 최종 결과물 반환 (딕셔너리 형태)
    # ==========================================
    return {
        "summary": {
            "risk_preference": risk_pref,
            "total_amt": total_amt,
            "grnt_ratio": grnt_ratio,
            "ungrnt_ratio": ungrnt_ratio
        },
        "guaranteed": grnt_results,
        "non_guaranteed": notgrnt_results
    }

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
        context += f"{i+1}위. {p['name']} (점수: {p['score']}점) - 특징: {reasons_text}\n"

    context += "\n[실적 배당형(비보장형) 추천]\n"
    for i, p in enumerate(portfolio["not_guaranteed"]):
        reasons_text = ", ".join(p["reasons"])
        context += f"{i+1}위. {p['name']} (점수: {p['score']}점) - 특징: {reasons_text}\n"

    return context

## 3단계: LLM 프롬프트 생성 (generate_bot_response)
# 최종적으로 사용자 질문과 2단계의 텍스트를 합쳐 AI에게 지시

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

    # 3. 우리가 쓸 AI 모델(Groq) 준비
    llm = ChatGroq(model="llama-3.3-70b-versatile")

    # 4. AI에게 프롬프트를 쏴주고(invoke) 결과 받기
    result = llm.invoke(system_prompt)

    # 지금은 테스트를 위해 프롬프트 자체를 출력해봅니다.
    return system_prompt

# 0. API 키 설정 (보안을 위해 환경 변수 사용)
import os
os.environ["GROQ_API_KEY"] = "put your APIkey"
api_key = os.getenv("GROQ_API_KEY")


import pandas as pd
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough



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
# 3. LLM 및 프롬프트 체인 (Chain) 세팅
# ==========================================
llm = ChatGroq(model="llama-3.3-70b-versatile")

prompt = ChatPromptTemplate.from_messages([
    ("system", """
너는 전문적이고 친절한 퇴직연금 AI 어드바이저다.

다음 규칙을 반드시 지켜라:
1. 상품명(예: TDF, ETF 등)이나 필수 금융 용어를 제외하고는 100% 자연스러운 한국어로 작성한다.
2. 고객에게 존댓말을 사용하며 신뢰감 있는 말투를 사용한다.
3. 제공된 [시스템 추천 사유]와 [검색된 상세 정보]만을 바탕으로 답변한다.
4. 고객의 질문에 직접적으로 답하면서, 왜 이 상품이 추천되었는지 명확히 설명한다.
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

# ==========================================
# 4. 최종 RAG 파이프라인 (rag_pipeline)
# ==========================================
def rag_pipeline(user_query, user, portfolio, vectorstore):
    """
    고객의 질문, 유저 정보, 추천된 포트폴리오를 받아 최종 AI 답변을 생성합니다.
    (portfolio는 get_portfolio_recommendation 함수의 반환값 딕셔너리입니다)
    """
    # 1. 포트폴리오에서 보장형과 비보장형 추천 상품을 하나의 리스트로 합칩니다.
    all_recs = portfolio["guaranteed"] + portfolio["non_guaranteed"]

    # 2. 추천된 상품들의 ID만 쏙쏙 뽑아냅니다. (이 ID로만 RAG 검색을 할 겁니다)
    candidate_ids = [r["product_info"]["product_id"] for r in all_recs]

    # 3. RAG 검색 실행
    retrieved_docs = retrieve_with_filter(user_query, candidate_ids, vectorstore)
    rag_text = "\n\n".join([d.page_content for d in retrieved_docs])

    # 4. LLM에게 넘겨줄 텍스트(Context) 조립하기
    reason_text = "[시스템 추천 사유]\n"
    for r in all_recs:
        p_name = r["product_name"]
        reasons = "\n  - ".join(r["reasons"])
        reason_text += f"■ {p_name} (추천 점수: {r['score']}점)\n  - {reasons}\n\n"

    final_context = reason_text + "[검색된 상세 정보(약관/스펙)]\n" + rag_text

    # 5. LLM 체인 실행 및 답변 받기
    result = chain.invoke({
        "context": final_context,
        "user": user,
        "user_query": user_query
    })

    return result.content

# 1. 문서화 및 임베딩 도구 불러오기 (이미 하셨다면 생략 가능)
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

# 2. 문서 만들기 (이전에 만드신 merged_df 사용)
docs = build_documents(merged_df)

# 3. 임베딩 모델 준비 (문장을 벡터 숫자로 바꿔주는 AI)
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 4. vectorstore 생성
vectorstore = FAISS.from_documents(docs, embedding)

print("✅ Vector DB(도서관) 구축 완료! 이제 챗봇을 실행해도 됩니다.")


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


llm = ChatGroq(model="llama-3.3-70b-versatile")

prompt = ChatPromptTemplate.from_messages([
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

save_path = "/content/drive/MyDrive/FiChat/faiss_index"

# 1. 임베딩 모델 준비
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2. 저장해둔 도서관(faiss_index) 파일 불러오기
# 주의: 최신 LangChain에서는 보안상 allow_dangerous_deserialization=True 를 꼭 적어줘야 합니다.
vectorstore = FAISS.load_local(save_path, embedding, allow_dangerous_deserialization=True)

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


def chatbot(user_input, user, session_id, vectorstore, top_n=5):

    # 2. 추천
    portfolio = get_portfolio_recommendation(user, grnt_df, notgrnt_df, top_n)


    # 3. 🔥 RAG pipeline 호출
    response = rag_pipeline(
        user_query=user_input,
        user=user,
        portfolio=portfolio,
        vectorstore=vectorstore
    )

    return response, user, portfolio

import difflib

# 퇴직연금사업자 목록 추출 (한 번만)
all_operators = grnt_df["pension_operator"].dropna().unique().tolist()






