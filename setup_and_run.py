import os
import subprocess
import time

def run_cmd(cmd):
    print(f"실행 중: {cmd}")
    return subprocess.run(cmd, shell=True)

# 1. 필수 폴더들 한꺼번에 만들기
folders = ['agents', 'tasks', 'outputs', 'tools']
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"폴더 생성 완료: {folder}")

# 2. 필수 라이브러리 자동 설치
print("라이브러리 설치를 시작합니다. 잠시만 기다려주세요...")
run_cmd("pip install crewai langchain-community langchain-google-genai python-dotenv")

# 3. 테스트용 main.py 자동 생성
main_code = """
from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama

# 1. 내 컴퓨터의 Gemma 4 연결
local_llm = Ollama(model="gemma4")

# 2. 비즈니스 에이전트 설정
strategist = Agent(
    role='비즈니스 전략 기획가',
    goal='디지털 상품의 타겟 분석 및 브랜드 네이밍 제안',
    backstory='무자본 지식 창업 전문가입니다.',
    llm=local_llm,
    verbose=True
)

# 3. 미션 부여
mission = Task(
    description="1인 기업가를 위한 'AI 자동화 챌린지' 타겟 3곳과 브랜드 이름 3개를 한국어로 제안해줘.",
    expected_output="비즈니스 제안 리포트",
    agent=strategist
)

# 4. 실행
crew = Crew(agents=[strategist], tasks=[mission])
print("\\n🚀 AI 에이전트가 첫 업무를 시작합니다...\\n")
print(crew.kickoff())
"""

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code.strip())
print("main.py 생성이 완료되었습니다.")

# 4. 바로 실행 시도
print("\\n환경 세팅 완료! 첫 번째 업무를 시도합니다...")
run_cmd("python main.py")