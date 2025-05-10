import streamlit as st
import requests

API_KEY = st.secrets["DEEPSEEK_API_KEY"]
API_URL = "https://api.deepseek.com/v1/chat/completions"

def call_deepseek(prompt, temperature=0.7):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位擅長爽文小說創作的編劇。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }
    response = requests.post(API_URL, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ 請求失敗：{response.status_code} - {response.text}"
