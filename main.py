# CrewAI 핵심 구성 요소 import
from crewai import Agent, Task, Crew, LLM

# 3No Theory 점수 계산 및 유형/추천 로직 import
from diagnosis_logic import calculate_scores, diagnose, classify_type, recommend_product

# 1. 내 컴퓨터의 Ollama(Gemma4) 모델 연결
# → CrewAI가 사용할 LLM 설정
local_llm = LLM(
    model="ollama/gemma4",
    base_url="http://localhost:11434"
)


# 2-1. 실행 전략 에이전트
# → 진단 결과를 바탕으로 부모의 다음 행동을 설계하는 역할
strategist = Agent(
    role='부모 성장 실행 설계가',
    goal='진단 결과를 바탕으로 부모가 바로 실천할 수 있는 회복 및 실행 전략을 설계한다',
    backstory='행복대물림OS와 3No Theory를 바탕으로 부모가 무너지지 않도록 구조와 루틴을 설계하는 전문가입니다.',
    llm=local_llm,
    verbose=True
)

# 2-2. 진단 에이전트 (추가된 부분)
# → 앞으로 "3No Theory 기반 진단" 담당
# → 아직 실행에는 연결 안 된 상태 (다음 단계에서 연결 예정)
diagnostician = Agent(
    role="부모 구조 진단가",
    goal="사용자의 상태를 3No Theory 기준으로 구조적으로 진단한다.",
    backstory="행복대물림OS와 3No Theory를 바탕으로 부모가 어디서 먼저 무너지는지 해석하는 전문가입니다.",
    llm=local_llm,
    verbose=True
)

# 2-3. 콘텐츠 생성 에이전트
# → 실행 전략을 실제 콘텐츠로 변환하는 역할
content_creator = Agent(
    role='부모 성장 콘텐츠 제작자',
    goal='전략을 기반으로 실제 인스타그램 콘텐츠를 작성한다',
    backstory='부모성장연구소의 메시지를 현실적인 언어로 풀어내는 콘텐츠 전문가입니다.',
    llm=local_llm,
    verbose=True
)


# 테스트용 응답 (실제는 폼에서 들어올 값)
answers = [
    4,4,4,3,3,4,   # Energy
    3,4,3,4,3,2,   # Compass
    4,3,4,3,2,2    # Action
]

# 점수 계산
scores = calculate_scores(answers)
result = diagnose(scores)


# 3-1. 진단 작업
diagnosis_task = Task(
    description=f"""
다음은 부모의 3No Theory 점수 기반 진단 데이터입니다.

점수:
- Energy: {scores['Energy']}
- Compass: {scores['Compass']}
- Action: {scores['Action']}

1차 진단 결과:
{result}

유형:
{classify_type(scores)}

추천 리소스:
- 매거진: {recommend_product(classify_type(scores))['magazine']}
- 가이드: {recommend_product(classify_type(scores))['guide']}
- 상품: {recommend_product(classify_type(scores))['product']}

이 데이터를 바탕으로 아래 형식으로 구조 진단을 수행하세요.

출력 형식:
1. 가장 우선되는 진단 축 1개
2. 왜 그렇게 진단했는지 3문장 이내 설명
3. 지금 가장 먼저 멈춰야 할 것 1개
4. 지금 가장 먼저 세워야 할 것 1개
5. 오늘 바로 할 수 있는 것 1개
""",
    expected_output="3No Theory 기반 부모 구조 진단 결과",
    agent=diagnostician
)

# 3-2. 진단 결과를 바탕으로 실행 전략 설계
strategy_task = Task(
    description="""
이전 진단 결과를 바탕으로, 부모가 실제로 삶을 개선할 수 있는 실행 전략을 설계해주세요.

출력 형식:
1. 핵심 문제 요약 1문장
2. 가장 먼저 집중해야 할 영역 1개
3. 7일 실행 루틴 제안
4. 절대 하지 말아야 할 행동 1개
5. 이 사람이 지금 가장 필요로 하는 방향성 한 줄

조건:
- 감성 위로 금지
- 실행 가능한 내용만 제시
- 부모성장연구소 톤앤매너 유지
""",
    expected_output="실행 전략 설계",
    agent=strategist,
    context=[diagnosis_task]  # ← 이 한 줄이 핵심
)


# 4. Crew 구성
# → 현재는 부모 구조 진단가만 참여
crew = Crew(
    agents=[diagnostician, strategist],  # ← 두 개 다 넣기
    tasks=[diagnosis_task, strategy_task]  # ← 순서 중요 (진단 → 전략)
)


# 5. 실행
print("\n🚀 AI 에이전트가 첫 업무를 시작합니다...\n")
print(crew.kickoff())