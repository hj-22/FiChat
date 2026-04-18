# 설문 내용
# 각 키값(experience, psychology 등)은 user_profile의 필드명과 일치시킵니다.
SURVEY_CONTENT = {
    "experience": {
        "label": "투자 경험을 기준으로 본인의 수준은 어느 정도인가요? (여러 경험이 있다면 가장 높은 위험 수준을 선택해주세요)",
        "options": [
            "1. 고위험 투자(파생상품, 레버리지 투자 등 변동성이 큰 투자) 경험이 있음",
            "2. 주식 투자(주식 또는 원금 비보장 상품) 경험이 있음",
            "3. 펀드, ETF 등 간접투자 경험이 있음",
            "4. 안정형 금융상품(채권, 채권형 펀드) 투자 경험이 있음",
            "5. 예적금 위주로 금융상품 이용",
            "6. 투자 경험 없음"
        ]
    },
    "psychology": {
        "label": "투자 손실이 발생했을 때 어떻게 행동하시겠습니까?",
        "options": [
            "1. 추가 투자하여 손실 회복을 시도한다.",
            "2. 당장 매도하지 않고 상황을 지켜본다.",
            "3. 손실 확대를 막기 위해 안전자산으로 옮긴다."
        ]
    },
    "loss_tolerance": {
        "label": "감내 가능한 손실 수준은 어느 정도인가요?",
        "options": [
            "1. 원금 보존",
            "2. 최소한의 손실만 (5% 이내) 감수",
            "3. 일부 손실 (5~15%) 감수 가능",
            "4. 수익이 높다면 위험은 상관 없음"
        ]
    },
    "knowledge": {
        "label": "투자상품을 선택할 때 본인 수준에 가장 가까운 것을 선택해주세요.",
        "options": [
            "1. 상품 구조와 위험을 직접 비교하고 투자 결정을 할 수 있다. (예: 수익률, 위험도, 수수료 비교)",
            "2. 상품 설명을 읽으면 위험 수준은 이해할 수 있지만 투자 결정은 어렵다",
            "3. 기본적인 상품(예금, 펀드 등)은 이해하지만 복잡한 상품은 어렵다",
            "4. 상품 설명을 읽어도 이해하기 어려워 추천에 의존한다"
        ]
    },
    "goal": {
        "label": "주된 투자 목적은 무엇인가요?",
        "options": [
            "1. 자산 증식",
            "2. 노후 준비",
            "3. 예적금보다 높은 수익",
            "4. 세액공제"
        ]
    },
    "pension_ratio": {
        "label": "전체 노후 자산 중 퇴직연금이 차지하는 비중이 어느 정도인가요?",
        "options": [
            "1. 10% 미만",
            "2. 10~40%",
            "3. 40~70%",
            "4. 70% 이상"
        ]
    },
    "income_future": {
        "label": "향후 수입원에 대한 예상은 어떠신가요?",
        "options": [
            "1. 현재 소득이 일정하며, 향후 상당 기간 유지 또는 증가 예상",
            "2. 현재 소득은 일정하지만, 향후 감소하거나 불안정할 것으로 예상",
            "3. 현재 일정한 소득이 없음"
        ]
    },
    "direct_manage": {
        "label": "선호하는 투자 관리 방식은 무엇인가요?",
        "options": [
            "1. 내가 직접 관리",
            "2. 전문가에게 맡김"
        ]
    }
}

# 설문 단계 정의 (순서, 키, 라벨, 위젯 타입)
SURVEY_STEPS = [
    {"key": "age", "label": "나이(만 나이 기준)", "type": "number"},
    {"key": "period", "label": "은퇴까지 남은 기간(년)", "type": "number"},
    {"key": "experience", "label": None, "type": "radio"},
    {"key": "psychology", "label": None, "type": "radio"},
    {"key": "loss_tolerance", "label": None, "type": "radio"},
    {"key": "knowledge", "label": None, "type": "radio"},
    {"key": "goal", "label": None, "type": "radio"},
    {"key": "pension_ratio", "label": None, "type": "radio"},
    {"key": "income_future", "label": None, "type": "radio"},
    {"key": "investment_amount", "label": "투자금액(DC 연금계좌에 적립된 퇴직금 금액/만원)", "type": "number"},
    {"key": "pension_operator", "label": "가입한 퇴직연금사업자", "type": "text_match"},
    {"key": "direct_manage", "label": None, "type": "radio"}
]