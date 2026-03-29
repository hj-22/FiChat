# 흐름: db에서 가입 사업자 기준으로 먼저 필터링해서 가져오기
# 이후 가져온 데이터로 계산
from models import SurveyAnswers
from user_profile import build_user_profile
from recommender import get_categorized_products, get_portfolio_recommendation


# ========== 유저 정보 생성 ========== #

# 예시 입력ㅇ빈다
inputs: SurveyAnswers = {
    "name": "익명",
    "age": 30,
    "period": 10,
    "experience": 3,
    "psychology": 2,
    "loss_level": 1,
    "finance_knowledge": 2,
    "investment_goal": 3,
    "rate_of_investment": 1,
    "expected_income": 4,
    "investment_amount": 5000000,
    "pension_operator": ["KB국민은행", "미래에셋증권"],
    "direct_manage": True
}

user_profile = build_user_profile(inputs)
grnt_df, notgrnt_df = get_categorized_products(user_profile)

recommendations = get_portfolio_recommendation(user_profile, grnt_df, notgrnt_df)
