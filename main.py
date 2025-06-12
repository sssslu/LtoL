import time
from datetime import datetime

# ========== 파일 이름 설정 ==========
TOPIC_LOG_FILE = "topics.txt"
LOG_FILE = f"debate_{datetime.now().date()}.txt"
MAX_TURNS = 10  # 총 10차례 발언 (5턴씩)

# ========== 파일 입출력 함수 ==========
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

# ========== 주제 생성 ==========
def generate_new_topic(previous_topics):
    prompt = f"""지금까지 사용한 주제 목록:
{chr(10).join(f"- {t}" for t in previous_topics)}

이 목록과 중복되지 않는 새로운 과학 또는 사회 관련 대화 주제를 하나 추천해줘."""
    # TODO: GPT API 호출로 대체
    return "AI가 예술 창작에 끼치는 영향은 무엇일까?"

# ========== 프롬프트 생성 ==========
def build_prompt(log, last_message, role):
    return f"""주제: {TOPIC}

지금까지의 대화:
{log}

마지막에 상대방이 이렇게 말했습니다:
"{last_message}"

당신({role})은 자연스럽게 이어서 대화하세요. 흥미로운 관점을 공유하거나 상대방에게 다시 질문을 던져도 좋습니다.

당신의 다음 말은?"""

# ========== API 호출 대행 (샘플) ==========
def call_chatgpt(prompt):
    # TODO: OpenAI ChatGPT API로 교체
    return "ChatGPT의 응답 예시"

def call_gemini(prompt):
    # TODO: Gemini API 호출로 교체
    return "Gemini의 응답 예시"

# ========== 메인 루프 ==========
def main():
    global TOPIC
    previous_topics = get_previous_topics()
    TOPIC = generate_new_topic(previous_topics)
    save_new_topic(TOPIC)

    print(f"오늘의 대화 주제: {TOPIC}")
    append_to_log(f"[주제] {TOPIC}")

    last_message = "이 주제에 대해 이야기해볼까요?"

    for turn in range(MAX_TURNS):
        is_gpt_turn = (turn % 2 == 0)
        role = "ChatGPT" if is_gpt_turn else "Gemini"
        log = read_log()
        prompt = build_prompt(log, last_message, role)

        if is_gpt_turn:
            reply = call_chatgpt(prompt)
        else:
            reply = call_gemini(prompt)

        append_to_log(f"{role}: {reply}")
        last_message = reply
        time.sleep(1)  # 자연스러움 또는 쿨타임 대용

if __name__ == "__main__":
    main()
