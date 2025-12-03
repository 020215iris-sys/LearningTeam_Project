# openai_client.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# .env에서 환경변수 로드
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY 가 설정되어 있지 않습니다. .env 파일을 확인하세요.")

# test_openai.py에서 썼던 방식과 동일하게 클라이언트 생성
client = OpenAI(
    api_key=API_KEY,
    timeout=15,   # 테스트에서 잘 돌아갔던 값
)

def ask_openai(messages):
    """
    messages: [{"role": "system" | "user" | "assistant", "content": "..."}] 리스트
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",   # mini 모델 사용
        messages=messages,
        max_tokens=512,        # 이때는 넉넉하게 512로 사용했음
    )

    choice = resp.choices[0]

    # SDK 버전에 따라 dict / object 차이가 있어서 방어적으로 처리
    content = getattr(choice.message, "content", None)
    if content is None and isinstance(choice.message, dict):
        content = choice.message.get("content", "")

    return content
