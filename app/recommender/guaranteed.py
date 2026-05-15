"""
원금보장형 상품을 추천하고 이유를 제시합니다.
"""

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


def generate_reasons(df, product, user):
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