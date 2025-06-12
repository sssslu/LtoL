import os
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

# ====== .env 로드 ======
print(">> 환경 변수 로드 중...")
load_dotenv()
GPT_API_KEY = os.getenv("gptKey")
GEMINI_API_KEY = os.getenv("geminiKey")

# ====== 클라이언트 설정 ======
print(">> API 클라이언트 설정 중...")
client = OpenAI(api_key=GPT_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# ====== 파일 설정 ======
TOPIC_LOG_FILE = "topics.txt"
LOG_FILE = f"debate_{datetime.now().date()}.txt"
MAX_TURNS = 5

# ====== 파일 I/O ======
def append_to_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n\n")

def read_log():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def get_previous_topics():
    try:
        with open(TOPIC_LOG_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def save_new_topic(topic):
    with open(TOPIC_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(topic + "\n")

# ====== 주제 생성 ======
def generate_new_topic(previous_topics):
    topic_list = "\n".join(f"- {t}" for t in previous_topics)
    prompt = f"""다음은 지금까지 사용된 주제입니다:

{topic_list}

이 목록과 겹치지 않도록, 흥미로운 과학 또는 사회 관련 대화 주제를 하나만 추천해주세요. 짧고 명확하게."""
    print(">> GPT에게 주제 요청 중...")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 독창적이고 통찰력 있는 대화 주제를 추천하는 AI입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
    )
    topic = response.choices[0].message.content.strip()
    print(f">> GPT 주제 응답 완료: {topic}")
    return topic

# ====== 프롬프트 생성 ======
def build_prompt(topic, log, last_message, role, turn):
    closing_hint = ""
    if turn >= MAX_TURNS - 2:
        closing_hint = "이번 대화는 곧 마무리될 예정입니다. 자연스럽게 정리하거나 마무리 발언을 해주세요."

    return f"""주제: {topic}

지금까지의 대화:
{log}

상대방이 마지막으로 이렇게 말했습니다:
"{last_message}"

당신({role})은 자연스럽게 대화를 이어가세요. 새로운 관점을 제시하거나 질문해도 좋습니다.
{closing_hint}

당신의 다음 말은?
"""


# ====== GPT 응답 (최신 방식) ======
def call_chatgpt(prompt):
    print(">> ChatGPT 호출 중...")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 친근하고 지적인 AI로서, 자연스럽고 유익한 대화를 이어갑니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    reply = response.choices[0].message.content.strip()
    print(">> ChatGPT 응답 완료")
    return reply
def call_gemini(prompt):
    print(">> Gemini 호출 중...")
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        chat = model.start_chat()  # history는 생략
        response = chat.send_message(prompt)

        # 안정적인 텍스트 추출
        if hasattr(response, "text"):
            reply = response.text.strip()
        else:
            reply = response.candidates[0].content.parts[0].text.strip()

        print(">> Gemini 응답 완료")
        return reply

    except Exception as e:
        print(f"!! Gemini 오류 발생: {e}")
        return f"[Gemini 오류: {e}]"


def main():
    print(">> 이전 주제 목록 불러오는 중...")
    previous_topics = get_previous_topics()

    print(">> 새로운 주제 생성 중...")
    topic = generate_new_topic(previous_topics)
    save_new_topic(topic)

    print(f"\n오늘의 대화 주제: {topic}")
    append_to_log(f"[주제] {topic}")
    print(">> 주제 로그 저장 완료")

    last_message = "이 주제에 대해 이야기해볼까요?"

    for turn in range(MAX_TURNS):
        print(f"\n== {turn+1}/{MAX_TURNS}턴 시작 ==")
        is_gpt_turn = (turn % 2 == 0)
        role = "ChatGPT" if is_gpt_turn else "Gemini"
        print(f">> 현재 역할: {role}")

        log = read_log()
        print(">> 로그 읽기 완료")

        prompt = build_prompt(topic, log, last_message, role, turn)
        print(">> 프롬프트 생성 완료")

        try:
            if is_gpt_turn:
                reply = call_chatgpt(prompt)
            else:
                reply = call_gemini(prompt)
        except Exception as e:
            reply = f"[에러 발생: {e}]"
            print(f"!! 오류 발생: {e}")

        append_to_log(f"{role}: {reply}")
        print(">> 응답 저장 완료")
        last_message = reply
        time.sleep(1)

    print("\n>> 모든 턴 종료. 대화 완료.")

if __name__ == "__main__":
    
    main()
