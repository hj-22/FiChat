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

def risk_preference_question(age, period, experience, psychology, loss_level, finance_knowledge,
                             investment_goal, rate_of_investment, expected_income):
    score = 0
    #나이
    if age >= 19 and age <= 34:
        score += 10
    elif age >= 35 and age <= 44:
        score += 8
    elif age >= 45 and age <= 54:
        score += 6
    elif age >= 55 and age <= 64:
        score += 4
    else:
        score += 2

    #은퇴까지 남은 기간
    if period >= 10:
        score += 15
    elif period >= 5 and period <10:
        score += 12
    elif period >= 3 and period < 5:
        score += 8
    elif period >= 1 and period <3:
        score += 4
    else:
        score += 2

    #투자 경험
    if  experience == 1:
        score += 15
    elif experience == 2:
        score += 12
    elif experience == 3:
        score += 9
    elif experience == 4:
        score += 6
    elif experience == 5:
        score += 3
    else:
        score += 1

    #투자 심리
    if psychology == 1:
        score += 10
    elif psychology == 2:
        score += 5
    else:
        score += 1

    # 감내할 수 있는 손실수준
    if loss_level == 1:
        return "안정형"
    elif loss_level == 2:
        score += 8 #위험중립형 이하 추가해야 함
    elif loss_level == 3:
        score += 14
    elif loss_level == 4:
        score += 20

    #금융지식 수준/이해도
    if finance_knowledge == 1:
        score += 10
    elif finance_knowledge == 2:
        score += 7
    elif finance_knowledge == 3:
        score += 4
    else:
        score += 1

    #투자목적
    if investment_goal == 1:  #자산 증식
        score += 5
    elif investment_goal == 2:  #노후 준비를 위한 운용
        score += 4
    elif investment_goal == 3:  #예적금보다 높은 수익 기대
        score += 2
    elif investment_goal == 4:  # 세액공제
        score += 1

    #전체 노후 자산 중에서 퇴직연금이 차지하는 비중
    if rate_of_investment == 1:
        score += 10
    elif rate_of_investment == 2:
        score += 7
    elif rate_of_investment == 3:
        score += 4
    else:
        score += 1

    #향후 수입원에 대한 예상
    if expected_income == 1:
        score += 5
    elif expected_income == 2:
        score += 3
    else:
        score += 1

    #점수기반 투자성향 구분
    if score <= 30:
        return "안정형"
    elif score >=31 and score <= 50:
        return "안정추구형"
    elif score >= 51 and score <= 70:
        return "위험중립형"
    elif score >= 71 and score <= 90:
        if loss_level == 2:
            return "위험중립형"
        return "적극투자형"
    else:
        if loss_level == 2:
            return "위험중립형"
        return "공격투자형"

######################################################
##############       점수계산 - 보장형      ##############
######################################################
def add_product_type(df):
    safe_product = ["정부보증채","은행 예적금", "증권금융회사 예탁금"]
    risky_product = ["저축은행 예적금", "발행어음 및 표지어음", "원리금파생상품결합사채",
                     "금리연동형 보험", "이율보증형 보험", "환매조건부 매수계약"]

    df["is_safe"] = df["product_name"].apply(
        lambda x: any(k in x for k in safe_product)
    )
    df["is_risky"] = df["product_name"].apply(
        lambda x: any(k in x for k in risky_product)
    )

    return df

def get_risk_score(df, user):
    risk = user["risk_preference"]

    safe_map = {
        "안정형": 100,
        "안정추구형": 80,
        "위험중립형": 60,
        "적극투자형": 40,
        "공격형": 20
    }

    risky_map = {
        "안정형": 20,
        "안정추구형": 40,
        "위험중립형": 60,
        "적극투자형": 80,
        "공격형": 100
    }

    df["product_score"] = 0

    df.loc[df["is_safe"], "product_score"] = safe_map.get(risk, 60)
    df.loc[df["is_risky"], "product_score"] = risky_map.get(risk, 60)

    return df


def get_risk_score(df, user):
    risk = user["risk_preference"]

    safe_map = {
        "안정형": 100,
        "안정추구형": 80,
        "위험중립형": 60,
        "적극투자형": 40,
        "공격형": 20
    }

    risky_map = {
        "안정형": 20,
        "안정추구형": 40,
        "위험중립형": 60,
        "적극투자형": 80,
        "공격형": 100
    }

    df["product_score"] = 0

    df.loc[df["is_safe"], "product_score"] = safe_map.get(risk, 60)
    df.loc[df["is_risky"], "product_score"] = risky_map.get(risk, 60)

    return df


def get_rate_score(df, user):
    risk = user["risk_preference"]

    max_rate = df["interest_rate"].max()
    df["rate_level"] = df["interest_rate"] / max_rate * 100

    weight_map = {
        "안정형": 0.6,
        "안정추구형": 0.7,
        "위험중립형": 0.8,
        "적극투자형": 0.9,
        "공격형": 1.0
    }

    weight = weight_map.get(risk, 0.8)

    df["rate_score"] = df["rate_level"] * weight

    return df

def calculate_grnt_score(df, user):
    df = add_product_type(df)
    df = get_risk_score(df, user)
    df = get_rate_score(df, user)

    df["score"] = 0.7 * df["product_score"] + 0.3 * df["rate_score"]

    return df

# 점수계산- 보장형
def generate_reasons(product, user, df):
    reasons = []

    safe_product = ["정부보증채","은행 예적금", "증권금융회사 예탁금"]
    risky_product = ["저축은행 예적금", "발행어음 및 표지어음", "원리금파생상품결합사채",
                     "금리연동형 보험", "이율보증형 보험", "환매조건부 매수계약"]

    product_name = product["product_name"]
    risk = user["risk_preference"]

    if any(k in product_name for k in risky_product):
        if risk == "안정형":
            reasons.append("위험 선호 성향과 차이가 있습니다.")
        elif risk == "안정추구형":
            reasons.append("위험 선호 성향과 일부 차이가 있습니다.")
        elif risk == "위험중립형":
            reasons.append("위험 선호 성향과 일부 일치합니다.")
        elif risk == "적극투자형":
            reasons.append("위험 선호 성향과 전반적으로 일치합니다.")
        else:
            reasons.append("위험 선호 성향과 일치합니다.")

    elif any(k in product_name for k in safe_product):
        if risk == "안정형":
            reasons.append("위험 선호 성향과 일치합니다.")
        elif risk == "안정추구형":
            reasons.append("위험 선호 성향과 전반적으로 일치합니다.")
        elif risk == "위험중립형":
            reasons.append("위험 선호 성향과 일부 일치합니다.")
        elif risk == "적극투자형":
            reasons.append("위험 선호 성향과 일부 차이가 있습니다.")
        else:
            reasons.append("위험 선호 성향과 차이가 있습니다.")

    max_rate = df["interest_rate"].max()
    rate_level = product["interest_rate"] / max_rate * 100

    if rate_level >= 80:
        rate_desc = "동일 유형 상품 대비 금리가 유리한 편입니다"
    elif rate_level >= 50:
        rate_desc = "평균 수준의 금리를 제공하는 상품입니다"
    else:
        rate_desc = "금리는 다소 낮지만 안정성이 강조된 상품입니다"

    if risk == "안정형":
        reasons.append(
            f"원리금이 보장되는 안정적인 상품으로, {rate_desc} 포트폴리오의 안정성을 높이는 데 적합합니다"
        )

    elif risk == "안정추구형":
        reasons.append(
            f"안정성을 확보하면서도 {rate_desc} 포트폴리오에서 리스크를 낮추는 역할을 합니다"
        )

    elif risk == "위험중립형":
        reasons.append(
            f"{rate_desc} 안정적인 자산으로, 수익형 자산과 함께 균형 잡힌 포트폴리오 구성이 가능합니다"
        )

    elif risk == "적극투자형":
        reasons.append(
            f"수익성은 제한적이지만 {rate_desc} 포트폴리오의 변동성을 낮추는 안정 자산으로 활용할 수 있습니다"
        )

    else:
        reasons.append(
            f"원리금이 보장되는 상품으로, {rate_desc} 포트폴리오의 안정적인 기반을 제공합니다"
        )

    return reasons


######################################################
##############       점수계산 - 비보장형      ############
######################################################

import pandas as pd
import numpy as np
import re
from datetime import datetime

# ==========================================
# 1. 장기수익률(R) 계산 함수
# ==========================================
def calculate_R_score(df, is_silver_mode=False):
    """
    장기수익률(R) 점수를 계산하고 전체 데이터프레임에 파생 변수를 추가합니다.
    """
    df = df.copy()

    # 1. 수익률 항목 Cross-sectional Min-Max 정규화 (0~100 환산)
    return_cols = ['return_1y', 'return_3y', 'return_5y']

    for col in return_cols:
        col_min = df[col].min()
        col_max = df[col].max()

        # 최댓값과 최솟값이 같은 경우(분모가 0이 되는 것) 방지
        if col_max != col_min:
            df[f'norm_{col}'] = 100 * (df[col] - col_min) / (col_max - col_min)
        else:
            df[f'norm_{col}'] = 50.0 # 변별력이 없을 경우 중간값 부여

    # 2. 개별 상품의 장기수익률(R) 산출 로직
    def compute_R(row):
        r1 = row.get('norm_return_1y', np.nan)
        r3 = row.get('norm_return_3y', np.nan)
        r5 = row.get('norm_return_5y', np.nan)

        has_1y = pd.notna(r1)
        has_3y = pd.notna(r3)
        has_5y = pd.notna(r5)

        # 1년 수익률조차 없으면 0점 처리 (혹은 다른 예외 처리 필요)
        if not has_1y:
            return 0.0

        if is_silver_mode:
            # [실버 모드] 최근 시장 상황에 기민하게 대응
            if has_1y and has_3y and has_5y:
                return 0.6 * r1 + 0.2 * r3 + 0.2 * r5
            elif has_1y and has_3y and not has_5y:
                # 5년 데이터가 없을 때의 실버모드 비율 (0.6:0.2 -> 0.75:0.25 로 재분배)
                return 0.75 * r1 + 0.25 * r3
            else:
                return 1.0 * r1
        else:
            # [일반 모드] 장기 운용 성과 중시
            if has_1y and has_3y and has_5y:
                return 0.2 * r1 + 0.4 * r3 + 0.4 * r5
            elif has_1y and has_3y and not has_5y:
                return 0.3 * r1 + 0.7 * r3
            else:
                return 1.0 * r1

    # R 점수 적용
    df['score_R'] = df.apply(compute_R, axis=1)

    return df
# ==========================================
# 2. 위험등급(F) 계산 함수
# ==========================================
# 사용자 위험 성향별 상품 위험등급 점수 매트릭스
RISK_SCORE_MATRIX = {
    '공격투자형': {1: 100, 2: 100, 3: 100, 4: 80,  5: 60,  6: 30}, # ⭐️ 변수명 맞는지 확인
    '적극투자형': {1: 0,   2: 100, 3: 100, 4: 80,  5: 60,  6: 30},
    '위험중립형': {1: 0,   2: 0,   3: 100, 4: 100, 5: 80,  6: 60},
    '안정추구형': {1: 0,   2: 0,   3: 0,   4: 100, 5: 100, 6: 80},
    '안정형':     {1: 0,   2: 0,   3: 0,   4: 0,   5: 100, 6: 100}
}

def parse_risk_level(val):
    """'1등급' 형태의 텍스트에서 숫자만 추출"""
    match = re.search(r'\d+', str(val))
    if match:
        return int(match.group())
    return 6 # 에러 방지용 기본값 기본으로 가장 안전 자산이라고 가정 /근데 결측치는 없음

def calculate_F_score(df, user_risk_profile):
    df = df.copy()

    if user_risk_profile not in RISK_SCORE_MATRIX:
        user_risk_profile = '위험중립형' # 입력 오류 시 기본값

    scoring_dict = RISK_SCORE_MATRIX[user_risk_profile]

    df['parsed_risk'] = df['risk_level'].apply(parse_risk_level)
    df['score_F'] = df['parsed_risk'].map(scoring_dict)

    # 0점 처리된 데이터(가입 불가 등급) 필터링이나 마킹을 원하시면 여기서 추가 가능합니다.

    return df

# ==========================================
# 3. TDF 적합도 계산 함수
# ==========================================
# 사용자 특성별 점수 매핑 딕셔너리
TDF_MAPPING = {
    'M': { # 자산관리 방식
        '전적으로 전문가에게 맡기고 싶다': 100,
        '조언을 받아 내가 결정하고 싶다': 50,
        '내가 직접 알아보고 투자하고 싶다': 0
    }
}

def calculate_T_score(df, user_M):
    """
    사용자의 자산관리 방식(M)을 바탕으로 TDF 적합도(T) 점수를 산출합니다.
    공식: T = ProductTDF * M_score
    """
    df = df.copy()

    # 1. UserTDFFit 계산 (자산관리 방식 M만 100% 반영)
    user_tdf_fit = TDF_MAPPING['M'].get(user_M, 50) # 기본값 50점

    # 2. ProductTDF 확인 (TDF 상품인지 여부)
    def is_tdf(row):
        eligible = str(row.get('eligible_tdf', 'X')).strip().upper()
        name = str(row.get('product_name', '')).upper()

        if eligible == 'O' or 'TDF' in name:
            return 1
        return 0

    df['ProductTDF'] = df.apply(is_tdf, axis=1)

    # 3. 최종 T 점수 산출
    df['score_T'] = df['ProductTDF'] * user_tdf_fit

    return df

# ==========================================
# 4. 수수료(C) 계산 함수
# ==========================================
def calculate_C_score(df):
    """
    수수료(보수)가 낮을수록 높은 점수를 부여하는 역방향 Min-Max 정규화 적용
    """
    df = df.copy()

    # 결측치가 있을 경우 가장 보수적인 평가(가장 높은 수수료=0점)를 위해 max값으로 채우는 것을 권장 - 결측치 없음
    fee_col = 'total_expense_ratio'
    fee_min = df[fee_col].min()
    fee_max = df[fee_col].max()

    if fee_max != fee_min:
        # 공식: 100 * (1 - (Fee_i - Fee_min) / (Fee_max - Fee_min))
        df['score_C'] = 100 * (1 - (df[fee_col] - fee_min) / (fee_max - fee_min))
    else:
        df['score_C'] = 50.0  # 모든 상품 수수료가 동일할 경우 예외 처리

    return df

# ==========================================
# 5. 순자산 규모(A) 계산 함수
# ==========================================
def calculate_A_score(df):
    """
    순자산 규모(total_net_worth)의 상대적 순위(Percentile)를 기준으로 점수 산출
    """
    df = df.copy()

    asset_col = 'total_net_worth'

    # 결측치 제외한 유효 데이터 개수(N) 산출
    N = df[asset_col].notna().sum()

    if N > 1:
        # Pandas의 rank()를 사용해 1부터 N까지의 순위를 구함 (method='average'로 동점자 처리)
        # 공식: 100 * (Rank(A_i) - 1) / (N - 1)
        ranks = df[asset_col].rank(method='average')
        df['score_A'] = 100 * (ranks - 1) / (N - 1)
    else:
        df['score_A'] = 50.0

    # 결측치는 0점 처리 (혹은 평균점수 부여 등 정책에 따라 수정 가능)
    df['score_A'] = df['score_A'].fillna(0)

    return df

# ==========================================
# 6. 설정기간(S) 계산 함수
# ==========================================
def calculate_S_score(df, reference_date=None):
    """
    상품 설정일(launch_date)로부터 경과한 기간에 따라 점수 부여
    """
    df = df.copy()

    # 기준일(오늘) 설정
    if reference_date is None:
        reference_date = pd.to_datetime('today')
    else:
        reference_date = pd.to_datetime(reference_date)

    # 날짜 형식 변환 및 운용 기간(년수) 계산
    df['launch_date_dt'] = pd.to_datetime(df['launch_date'], errors='coerce')
    df['years_active'] = (reference_date - df['launch_date_dt']).dt.days / 365.25

    # 이미지로 제공된 점수 매트릭스 적용
    def get_S_score(years):
        if pd.isna(years): return 0
        if years >= 10: return 100
        elif years >= 7: return 80
        elif years >= 5: return 60
        elif years >= 3: return 40
        elif years >= 1: return 20
        else: return 0

    df['score_S'] = df['years_active'].apply(get_S_score)

    return df

# ==========================================
#  통합 점수(Total Score) 계산 함수
# ==========================================
def calculate_notgrnt_score(df, user_M, user_risk_profile, is_silver_mode=False):
    """
    사용자의 입력값과 모드(일반/실버)를 바탕으로 최종 추천 점수를 계산합니다.
    """
    # 1. 개별 지표 계산
    df = calculate_R_score(df, is_silver_mode)            # 장기수익률
    df = calculate_F_score(df, user_risk_profile)         # 위험등급 (여기서만 R 사용)
    df = calculate_C_score(df)                            # 수수료
    df = calculate_A_score(df)                            # 순자산 규모
    df = calculate_S_score(df)                            # 설정기간
    df = calculate_T_score(df, user_M)                    # TDF 적합도 (M만 사용하도록 수정)

    # 2. 가중치 설정
    if is_silver_mode:
        weights = {'R': 0.28, 'F': 0.30, 'C': 0.15, 'T': 0.15, 'A': 0.08, 'S': 0.04}
    else:
        weights = {'R': 0.38, 'F': 0.20, 'C': 0.15, 'T': 0.15, 'A': 0.08, 'S': 0.04}

    # 3. 최종 점수 합산
    df['Total_Score'] = (
        (weights['R'] * df['score_R']) +
        (weights['F'] * df['score_F']) +
        (weights['C'] * df['score_C']) +
        (weights['T'] * df['score_T']) +
        (weights['A'] * df['score_A']) +
        (weights['S'] * df['score_S'])
    )

    df_sorted = df.sort_values(by='Total_Score', ascending=False).reset_index(drop=True)
    return df_sorted

def generate_notgrnt_reasons(row, user_info):
    """
    row: 스코어링이 완료된 데이터프레임의 한 행(row)
    user_info: build_user_profile() 로 생성된 사용자의 딕셔너리 정보
    """
    reasons = []

    # 유저 프로필에서 핵심 정보 추출
    risk_pref = user_info.get("risk_preference", "위험중립형")
    direct_manage = user_info.get("direct_manage", True)

    # period(남은 투자기간)를 기준으로 실버 모드(은퇴 임박) 해당 여부 판단 (예: 5년 이하)
    period = user_info.get("period", 10)
    is_silver = isinstance(period, (int, float)) and period <= 5

    # 1. 위험등급(F) 기반 설명
    score_F = row.get('score_F', 0)
    parsed_risk = row.get('parsed_risk', 6)

    if score_F == 100:
        reasons.append(f"고객님의 '{risk_pref}' 성향에 딱 맞는 위험등급({parsed_risk}등급)을 가진 상품입니다.")
    elif score_F >= 60:
        reasons.append(f"고객님의 '{risk_pref}' 성향과 전반적으로 부합하는 수준의 위험도를 가졌습니다.")
    elif score_F > 0:
        reasons.append("고객님의 성향 대비 다소 보수적이거나 위험도가 높지만, 포트폴리오 다변화 측면에서 긍정적입니다.")

    # 2. 장기수익률(R) 기반 설명
    score_R = row.get('score_R', 0)
    if score_R >= 80:
        reasons.append("동일 유형 상품 대비 장기(1·3·5년) 수익률 성과가 최상위 수준으로 매우 우수합니다.")
    elif score_R >= 50:
        reasons.append("시장 평균 이상의 양호하고 안정적인 장기 수익률을 기록하고 있습니다.")
    else:
        reasons.append("최근 수익률 성과는 보통 수준이나, 안정성 및 수수료 등 다른 지표가 뛰어납니다.")

    # 3. 수수료(C) 기반 설명
    score_C = row.get('score_C', 0)
    if score_C >= 80:
        reasons.append("총보수(수수료)가 매우 저렴하여, 연금처럼 장기 투자할 때 복리 효과를 극대화하기 좋습니다.")
    elif score_C >= 50:
        reasons.append("상품의 총보수가 시장 평균 수준으로 합리적입니다.")

    # 4. TDF 적합도(T) 기반 설명 (direct_manage 반영)
    score_T = row.get('score_T', 0)
    # TDF 상품이면서, 고객이 '알아서 굴려주길' 원할 때(direct_manage == False)
    if score_T > 0 and not direct_manage:
        reasons.append("자산을 직접 관리하기보다 전문가에게 맡기고자 하는 고객님의 니즈에 맞춘 TDF 상품으로, 생애주기에 맞춰 알아서 자산 비중을 조절해 주어 편리합니다.")

    # 5. 규모(A) 및 설정기간(S) 기반 설명
    score_A = row.get('score_A', 0)
    score_S = row.get('score_S', 0)
    if score_A >= 70 and score_S >= 60:
        reasons.append("설정된 지 오래되었고 순자산 규모가 커서, 위기 상황에서도 흔들림 없이 안정적인 운용을 기대할 수 있습니다.")

    # 6. 은퇴 임박 모드(실버 모드) 안내
    if is_silver:
        reasons.append(f"💡 [실버 모드 적용] 투자 여유 기간이 {period}년 이하이신 점을 고려하여, 최근 시장 변동성 방어와 자산 안정성에 더 높은 가중치를 두어 엄선했습니다.")

    return reasons