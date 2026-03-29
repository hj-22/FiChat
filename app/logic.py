# 전체 input반영한 유저 프로필 만들기
def build_user_profile(
    age, period, experience, psychology, loss_level, finance_knowledge,
    investment_goal, rate_of_investment, expected_income,
    risk_preference, investment_amount, pension_operator, direct_manage
):
    """
    사용자의 설문 응답 및 기본 정보를 바탕으로 통합 유저 프로필을 생성합니다.
    """
    return {
        # 1. 투자 성향 산출용 Raw 데이터 (챗봇의 개인화 대화 컨텍스트로 활용 가능)
        "age": age,
        "experience": experience,
        "psychology": psychology,
        "loss_level": loss_level,
        "finance_knowledge": finance_knowledge,
        "investment_goal": investment_goal,
        "rate_of_investment": rate_of_investment,
        "expected_income": expected_income,

        # 2. 추천 알고리즘 및 필터링용 핵심 데이터
        "risk_preference": risk_preference,  # "안정형", "안정추구형", "위험중립형", "적극투자형", "공격투자형"
        "period": period,                    # 투자 기간 / 은퇴까지 남은 기간 (예: 5, 10 등 숫자)
        "investment_amount": investment_amount, # 투자 금액
        "pension_operator": pension_operator,   # 가입한 퇴직연금사업자 (필터링용)
        "direct_manage": direct_manage          # True(직접 관리 선호), False(전문가/시스템 위임 선호)
    }


def asset_allocation(risk_preference):
    #원리금 보장
    if risk_preference == "안정형":
        return 0.85
    elif risk_preference == "안정추구형":
        return 0.75
    elif risk_preference == "위험중립형":
        return 0.60
    elif risk_preference == "적극투자형":
        return 0.45
    else:
        return 0.30
