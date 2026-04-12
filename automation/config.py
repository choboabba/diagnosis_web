# -*- coding: utf-8 -*-
"""
automation/config.py

이 파일은 자동화 프로젝트 전역에서 공통으로 사용하는
기본 설정값들을 모아두는 파일입니다.

왜 이 파일이 필요한가?
- 파일 경로를 여러 파일에 흩어놓으면 유지보수가 어려워집니다.
- 시트 이름, 로그 파일 경로, 템플릿 폴더 경로 등이 바뀌었을 때
  이 파일만 수정하면 전체 코드에 반영할 수 있습니다.
- 처음 보는 사람도 "이 프로젝트가 어떤 파일을 어디서 읽는지" 한눈에 파악할 수 있습니다.

이 파일에서 관리하는 대표 항목
- 프로젝트 루트 경로
- data / templates / logs / secrets 폴더 경로
- Google 서비스 계정 키 파일 경로
- Google Sheets 문서명
- 기본 워크시트명
- 로그 파일 경로
- 자동화 동작 시 사용하는 기본 상태값
"""

from pathlib import Path


# ------------------------------------------------------------
# 1. 프로젝트 루트 경로 설정
# ------------------------------------------------------------
# __file__ 은 현재 이 config.py 파일의 실제 위치를 의미합니다.
# 예를 들어 현재 파일 위치가:
# E:/coding/AI-agent/automation/config.py
# 라면,
# .resolve()는 절대경로로 바꿔주고,
# .parent 는 automation 폴더,
# .parent.parent 는 프로젝트 루트인 AI-agent 폴더가 됩니다.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------
# 2. 주요 폴더 경로 설정
# ------------------------------------------------------------
# 아래 경로들은 프로젝트 루트 기준으로 고정합니다.
# 나중에 다른 파일에서 이 값을 import 해서 재사용합니다.
AUTOMATION_DIR = PROJECT_ROOT / "automation"
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
LOGS_DIR = PROJECT_ROOT / "logs"
SECRETS_DIR = PROJECT_ROOT / "secrets"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


# ------------------------------------------------------------
# 3. 주요 데이터 파일 경로 설정
# ------------------------------------------------------------
# 자동화 로직에서 실제로 읽고 쓸 파일 경로입니다.
TAG_RULES_FILE = DATA_DIR / "tag_rules.json"
CONTENT_MAP_FILE = DATA_DIR / "content_map.csv"
PROCESSED_IDS_FILE = DATA_DIR / "processed_ids.json"

# 로그 파일 경로입니다.
LOG_FILE = LOGS_DIR / "agent.log"

# Google 서비스 계정 키 파일 경로입니다.
# 이 파일은 Google Sheets API 인증에 사용됩니다.
SERVICE_ACCOUNT_FILE = SECRETS_DIR / "service_account.json"


# ------------------------------------------------------------
# 4. Google Sheets 관련 설정
# ------------------------------------------------------------
# 아래 값은 현재 사용자가 만든 Google Sheets 문서명 기준입니다.
# 스프레드시트 파일명이 바뀌면 여기만 수정하면 됩니다.
SPREADSHEET_NAME = "column_DB"

# 기본 워크시트(탭) 이름입니다.
# 사용자가 현재 보이는 첫 번째 탭 이름을 그대로 쓰는 경우가 많아서
# 기본값은 "Sheet1"로 두되,
# 실제 탭 이름이 다르면 반드시 수정해야 합니다.
#
# 예:
# - "Sheet1"
# - "리드DB"
# - "응답시트"
#
# 주의:
# Google Sheets의 "파일명"과 "탭 이름"은 다를 수 있습니다.
WORKSHEET_NAME = "division"


# ------------------------------------------------------------
# 5. 자동화 기본 상태값 설정
# ------------------------------------------------------------
# 새 리드가 들어왔을 때 가장 먼저 갖는 상태값입니다.
DEFAULT_STATUS = "new"

# 처리 여부 기본값입니다.
DEFAULT_PROCESSED_VALUE = "N"

# 클릭/구매 관련 기본값입니다.
DEFAULT_CLICKED_VALUE = "N"
DEFAULT_CLICKED_COUNT = 0
DEFAULT_PURCHASED_VALUE = "N"

# 오류 발생 시 기록할 상태값입니다.
ERROR_STATUS = "error"


# ------------------------------------------------------------
# 6. 시트에서 사용하는 주요 컬럼명 정의
# ------------------------------------------------------------
# 컬럼명을 문자열로 코드 곳곳에 직접 쓰기 시작하면 오타가 날 확률이 높아집니다.
# 그래서 주요 컬럼명은 여기서 상수처럼 관리합니다.
COL_DIAGNOSIS_ID = "diagnosis_id"
COL_CREATED_AT = "created_at"
COL_NAME = "name"
COL_EMAIL = "email"
COL_PHONE = "phone"
COL_SOURCE = "source"
COL_CAMPAIGN = "campaign"

COL_RESULT_TYPE = "result_type"
COL_RESULT_SCORE = "result_score"
COL_EMOTION_SCORE = "emotion_score"
COL_HABIT_SCORE = "habit_score"
COL_STUDY_SCORE = "study_score"
COL_RELATIONSHIP_SCORE = "relationship_score"
COL_PRIMARY_PROBLEM = "primary_problem"

COL_TAG_PARENT_TYPE = "tag_parent_type"
COL_TAG_INTEREST = "tag_interest"
COL_TAG_URGENCY = "tag_urgency"
COL_TAG_STAGE = "tag_stage"
COL_TAG_OFFER = "tag_offer"
COL_ALL_TAGS = "all_tags"

COL_STATUS = "status"
COL_CLICKED = "clicked"
COL_CLICKED_COUNT = "clicked_count"
COL_CLICKED_LAST_LINK = "clicked_last_link"
COL_CLICKED_LAST_AT = "clicked_last_at"
COL_PURCHASED = "purchased"
COL_PURCHASED_PRODUCT = "purchased_product"
COL_PURCHASE_AMOUNT = "purchase_amount"
COL_LAST_ACTION_AT = "last_action_at"

COL_RECOMMENDED_MAGAZINE = "recommended_magazine"
COL_RECOMMENDED_GUIDE = "recommended_guide"
COL_RECOMMENDED_PRODUCT = "recommended_product"
COL_EMAIL_TEMPLATE_ID = "email_template_id"
COL_EMAIL_SUBJECT_DRAFT = "email_subject_draft"
COL_EMAIL_BODY_DRAFT = "email_body_draft"

COL_PROCESSED = "processed"
COL_PROCESSED_AT = "processed_at"
COL_ERROR_MESSAGE = "error_message"


# ------------------------------------------------------------
# 7. 필수 컬럼 목록
# ------------------------------------------------------------
# 이 목록은 나중에 sheets_client.py에서
# "현재 시트에 필요한 컬럼이 다 있는지 검사"할 때 사용할 수 있습니다.
REQUIRED_COLUMNS = [
    COL_DIAGNOSIS_ID,
    COL_NAME,
    COL_EMAIL,
    COL_RESULT_TYPE,
    COL_RESULT_SCORE,
    COL_EMOTION_SCORE,
    COL_HABIT_SCORE,
    COL_STUDY_SCORE,
    COL_RELATIONSHIP_SCORE,
    COL_TAG_PARENT_TYPE,
    COL_TAG_INTEREST,
    COL_TAG_URGENCY,
    COL_TAG_STAGE,
    COL_TAG_OFFER,
    COL_ALL_TAGS,
    COL_STATUS,
    COL_RECOMMENDED_MAGAZINE,
    COL_RECOMMENDED_GUIDE,
    COL_RECOMMENDED_PRODUCT,
    COL_EMAIL_TEMPLATE_ID,
    COL_EMAIL_SUBJECT_DRAFT,
    COL_EMAIL_BODY_DRAFT,
    COL_PROCESSED,
    COL_PROCESSED_AT,
    COL_ERROR_MESSAGE,
]


# ------------------------------------------------------------
# 8. 템플릿 파일명 매핑
# ------------------------------------------------------------
# email_template_id 값과 실제 템플릿 파일명을 연결합니다.
# 예:
# content_map.csv 에 email_result_a 가 들어 있으면
# 아래 설정을 통해 templates/email_result_a.txt 파일을 읽게 됩니다.
EMAIL_TEMPLATE_FILES = {
    "email_result_a": TEMPLATES_DIR / "email_result_a.txt",
    "email_result_b": TEMPLATES_DIR / "email_result_b.txt",
    "email_result_c": TEMPLATES_DIR / "email_result_c.txt",
}


# ------------------------------------------------------------
# 9. 기본 CTA 링크 설정
# ------------------------------------------------------------
# 현재는 실제 URL이 아직 확정되지 않았으므로 임시값으로 둡니다.
# 나중에 실제 결과 페이지 / 가이드 페이지 / 상품 페이지 URL이 정해지면 수정하면 됩니다.
DEFAULT_CTA_LINK = "[링크 미확정 - 나중에 실제 URL로 교체 예정]"


# ------------------------------------------------------------
# 10. 처리 대상 판별 기준
# ------------------------------------------------------------
# processed 컬럼이 아래 값이면 "아직 처리되지 않은 리드"로 간주합니다.
UNPROCESSED_VALUES = {"", "N", "n", None}


# ------------------------------------------------------------
# 11. 로그 메시지용 프로젝트 이름
# ------------------------------------------------------------
# 로그 파일에 어떤 프로젝트 로그인지 남길 때 사용할 수 있습니다.
PROJECT_NAME = "lead-automation-agent"


# ------------------------------------------------------------
# 12. 디렉터리 자동 생성 함수
# ------------------------------------------------------------
# 프로젝트를 다른 PC로 옮기거나 처음 세팅할 때
# 필요한 폴더가 없어서 오류가 나는 것을 막기 위해 사용합니다.
def ensure_directories() -> None:
    """
    자동화 운영에 필요한 주요 디렉터리가 없으면 생성합니다.

    이 함수는 프로그램 시작 시 한 번 호출하면 됩니다.
    """
    for directory in [DATA_DIR, TEMPLATES_DIR, LOGS_DIR, SECRETS_DIR, OUTPUTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 13. 설정값 확인용 함수
# ------------------------------------------------------------
# 초기에 경로가 제대로 잡혔는지 빠르게 점검할 때 유용합니다.
def get_config_summary() -> dict:
    """
    현재 주요 설정값을 딕셔너리 형태로 반환합니다.

    반환 목적:
    - 디버깅
    - 초기 세팅 확인
    - 로그 출력
    """
    return {
        "project_root": str(PROJECT_ROOT),
        "spreadsheet_name": SPREADSHEET_NAME,
        "worksheet_name": WORKSHEET_NAME,
        "tag_rules_file": str(TAG_RULES_FILE),
        "content_map_file": str(CONTENT_MAP_FILE),
        "processed_ids_file": str(PROCESSED_IDS_FILE),
        "service_account_file": str(SERVICE_ACCOUNT_FILE),
        "log_file": str(LOG_FILE),
    }