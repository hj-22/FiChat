import streamlit as st

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq



# 3. 임베딩 모델 준비 (문장을 벡터 숫자로 바꿔주는 AI)
@st.cache_resource
def get_embedding_model():
    """임베딩 모델 로드"""
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embedding


@st.cache_resource
def get_llm_model():
    """LLM 모델 로드"""
    return ChatGroq(model="llama-3.3-70b-versatile")


