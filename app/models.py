from typing import TypedDict, List

# 설문 응답 규격 (입력 데이터)
class SurveyAnswers(TypedDict):
    """
    투자성향 및 기본 정보 응답 데이터
    """
    name: str   # 유저 닉네임
    # --- 성향 계산 문항
    age: int
    period: int
    experience: int
    psychology: int
    loss_level: int
    finance_knowledge: int
    investment_goal: int
    rate_of_investment: int
    expected_income: int
    # --- 추가정보
    investment_amount: int
    pension_operator: List[str]
    direct_manage: bool


# 유저 정보
class User(SurveyAnswers):
    """
    기본 유저 프로필
    """
    risk_preference: str        # 도출된 투자 성향
    allocation_ratio: float # 자산 배분 비율

