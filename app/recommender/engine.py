import pandas as pd
import database
from models import User

# 1. DB에서 데이터를 가져옴
def get_categorized_products(user_profile: User):
    operator_list = user_profile['pension_operator']
    operators = ', '.join(['%s']*len(operator_list))

    # ========== 쿼리 작성 ========== #
    query = f"""
    SELECT DISTINCT
        i.id AS product_id,
        i.product_name,
        i.product_type,
        i.category,
        f.maturity,
        f.interest_rate,
        v.risk_level,
        v.eligible_tdf,
        v.launch_date,
        v.total_net_worth,
        v.total_expense_ratio,
        v.average_return_1y AS return_1y,
        v.average_return_3y AS return_3y,
        v.average_return_5y AS return_5y
    FROM product_info i
        JOIN product_mapping m ON i.id = m.product_id
        JOIN operator_info o ON m.operator_id = o.id
            AND o.operator_name IN ({operators})
    LEFT JOIN product_fixed f ON i.id = f.id
    LEFT JOIN product_variable v ON i.id = v.id
    """
    # ========== 꺼내오기 ========== #
    merged_df = database.get_data(query, tuple(operator_list))

    # 2. 계산에 쓰이는 숫자(Float)로 강제 변환
    # errors='coerce'를 넣으면, 숫자로 바꿀 수 없는 이상한 글자가 있어도 에러를 내는 대신 빈칸(NaN)으로 안전하게 바꿔줍니다.
    numeric_columns = [
        'interest_rate',
        'return_1y',
        'return_3y',
        'return_5y',
        'total_expense_ratio',
        'total_net_worth',
        'maturity'
    ]

    for col in numeric_columns:
        if col in merged_df.columns:
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')

    # 3. 문자를 숫자로 다 바꾼 후에, 빈칸(NaN)을 0으로 채워줍니다.
    merged_df = merged_df.fillna(0)

    # ==========================================
    # (이하 기존 코드와 동일) 보장/비보장 쪼개기
    # ==========================================
    grnt_df = merged_df[merged_df['category'] == 'GUARANTEED'].copy()
    notgrnt_df = merged_df[merged_df['category'] == 'NON_GUARANTEED'].copy()

    return grnt_df, notgrnt_df


