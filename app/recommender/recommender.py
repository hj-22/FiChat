#추천 함수

def get_portfolio_recommendation(user_info, grnt_df, notgrnt_df, top_n=5):
    """
    스코어 기반으로 보장형/비보장형 상품을 각각 top_n개씩 추천해 주는 통합 함수
    - user_info: 유저 프로필 딕셔너리
    - grnt_df: 보장형 상품 데이터프레임
    - notgrnt_df: 비보장형 상품 데이터프레임
    - top_n: 추천받고 싶은 상품 개수 (기본값 5)
    """

    # 1. 비보장형(notgrnt) 계산을 위한 유저 파라미터 추출
    risk_pref = user_info.get("risk_preference", "위험중립형")
    direct_manage = user_info.get("direct_manage", True)
    period = user_info.get("period", 10)

    user_M = '전적으로 전문가에게 맡기고 싶다' if not direct_manage else '내가 직접 알아보고 투자하고 싶다'
    is_silver_mode = True if isinstance(period, (int, float)) and period <= 5 else False

    # ==========================================
    # 2. 보장형 상품 스코어링 및 Top N 추출
    # ==========================================
    # 원본 훼손 방지를 위해 copy() 사용 권장
    grnt_scored = calculate_grnt_score(grnt_df.copy(), user_info)
    grnt_top = grnt_scored.sort_values(by="score", ascending=False).head(top_n)

    grnt_results = []
    for _, row in grnt_top.iterrows():
        reasons = generate_reasons(row, user_info)
        grnt_results.append({
            "product_name": row["product_name"],
            "score": round(row["score"], 2),
            "reasons": reasons,
            "product_info": row.to_dict() # 챗봇이나 프론트엔드에서 쓸 전체 정보
        })

    # ==========================================
    # 3. 비보장형 상품 스코어링 및 Top N 추출
    # ==========================================
    notgrnt_scored = calculate_notgrnt_score(notgrnt_df.copy(), user_M, risk_pref, is_silver_mode)
    # calculate_notgrnt_score 내부에 이미 내림차순 정렬이 되어 있으므로 head만 취함
    notgrnt_top = notgrnt_scored.head(top_n)

    notgrnt_results = []
    for _, row in notgrnt_top.iterrows():
        reasons = generate_notgrnt_reasons(row, user_info)
        notgrnt_results.append({
            "product_name": row["product_name"],
            "score": round(row["Total_Score"], 2),
            "reasons": reasons,
            "product_info": row.to_dict()
        })

    # ==========================================
    # 4. 최종 결과물 반환
    # ==========================================
    return {
        "guaranteed": grnt_results,
        "non_guaranteed": notgrnt_results
    }

#설명용 컨텍스트

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