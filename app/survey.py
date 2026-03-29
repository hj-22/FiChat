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