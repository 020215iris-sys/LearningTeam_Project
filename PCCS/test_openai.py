# test_openai.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
print("API_KEY 시작 10글자:", API_KEY[:10] if API_KEY else "없음")

client = OpenAI(api_key=API_KEY, timeout=15)

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "테스트"}],
    max_tokens=50,
)
print("응답 텍스트:", resp.choices[0].message.content)
