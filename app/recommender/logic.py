from user_profile import asset_allocation
from guaranteed import calculate_grnt_score, generate_reasons
from non_guaranteed import calculate_notgrnt_score, generate_notgrnt_reasons

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


# 설명용 컨텍스트
def build_context(recommendations):
    context = ""

    for r in recommendations:
        product = r["product"]
        reasons = "; ".join(r["reasons"])

        context += f"""
        상품명: {product["name"]}
        금리: {product["rate"]}
        위험도: {product["risk"]}
        추천 이유: {reasons}
        """

    return context


def detect_intent(user_input):
    if "비교" in user_input or "차이" in user_input:
        return "compare"
    return "recommend"


def build_comparison_context(recommendations):
    text = ""

    for r in recommendations:
        p = r["product"]

        text += f"""
        상품명: {p['name']}
        금리: {p['rate']}%
        위험도: {p['risk']}
        특징: {', '.join(r['reasons'])}
        """

    return text


