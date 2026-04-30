from recommender import get_portfolio_recommendation
from .rag import rag_pipeline, generate_questions


def chatbot(user_input, user, session_id, vectorstore, grnt_df, notgrnt_df, top_n=5):

    # 2. 추천
    portfolio = get_portfolio_recommendation(user, grnt_df, notgrnt_df, top_n)  # 딕셔너리로 반환됨


    # 3. 🔥 RAG pipeline 호출
    response = rag_pipeline(
        user_query=user_input,
        user=user,
        portfolio=portfolio,
        vectorstore=vectorstore
    )

    return response, user, portfolio
