# automation/tag_engine.py

from __future__ import annotations

from typing import Dict, List, Tuple

from automation.tag_definitions import (
    TYPE_TAGS,
    MODULE_TAGS,
    FRAMEWORK_TAGS,
    generate_display_tags,
)


TYPE_KEYWORDS: Dict[str, List[str]] = {
    "Type_NoEnergy": [
        "지쳤", "지치", "버겁", "힘들", "힘이 없", "무기력",
        "감정 소모", "소진", "번아웃", "피곤", "체력", "수면",
        "회복", "스트레스", "우울", "불안", "멘탈",
    ],
    "Type_NoCompass": [
        "방향", "기준", "원칙", "철학", "정체성", "가치관",
        "어떻게 해야", "뭘 해야", "무엇을 해야", "맞는지 모르",
        "혼란", "헷갈", "모르겠", "기준이 없", "방향이 없",
    ],
    "Type_NoAction": [
        "실천", "행동", "실행", "미루", "꾸준", "지속", "습관",
        "알지만", "아는데", "못 하", "안 되", "작심삼일",
        "루틴", "계속 못", "유지 못", "반복 실패",
    ],
}

MODULE_KEYWORDS: Dict[str, List[str]] = {
    "Module_ReviewJournal": [
        "복기", "기록", "일기", "오답노트", "되돌아보", "패턴 분석", "반성",
    ],
    "Module_TimeReuse": [
        "시간", "루틴", "일정", "타임테이블", "계획", "하루 관리", "시간표",
    ],
    "Module_MentalCare": [
        "감정", "화", "짜증", "우울", "불안", "스트레스", "멘탈", "마음",
    ],
    "Module_PhysicalCare": [
        "체력", "수면", "건강", "몸", "피곤", "신체", "컨디션",
    ],
    "Module_FamilyIdentity": [
        "가훈", "가족 규칙", "규칙", "철학", "가치관", "가족 기준", "정체성",
    ],
    "Module_ParentingBasics": [
        "육아 정보", "발달", "훈육", "기초 육아", "연령별", "전문지식", "논문",
    ],
    "Module_Communication": [
        "대화", "말투", "소통", "대본", "어떻게 말", "훈육 멘트", "대화법",
    ],
    "Module_RelationshipRecovery": [
        "관계", "화해", "용서", "갈등", "서운", "거리감", "회복",
    ],
    "Module_Setup": [
        "정리", "정돈", "청소", "집안", "환경", "물건", "어수선",
    ],
    "Module_FinanceManagement": [
        "돈", "지출", "가계부", "예산", "장보기", "소비", "재정",
    ],
}

FRAMEWORK_KEYWORDS: Dict[str, List[str]] = {
    "Framework_Awareness": [
        "알고 싶", "문제가 뭔지", "왜 이런지", "진단", "이해", "파악",
    ],
    "Framework_Recovery": [
        "회복", "버티기", "지쳤", "힘들", "소진", "무너", "살려",
    ],
    "Framework_SkillTraining": [
        "배우", "연습", "훈련", "익히", "기술", "방법", "대본",
    ],
    "Framework_Optimization": [
        "유지", "꾸준", "습관", "정착", "최적화", "내면화", "루틴화",
    ],
    "Framework_Legacy": [
        "대물림", "이어", "가족 문화", "우리 집 문화", "다음 세대", "전해",
    ],
}


DEFAULT_TYPE = "Type_NoAction"
DEFAULT_MODULE = "Module_Communication"
DEFAULT_FRAMEWORK = "Framework_Awareness"


def _score_text(text: str, keyword_map: Dict[str, List[str]]) -> Dict[str, int]:
    scores: Dict[str, int] = {key: 0 for key in keyword_map}
    lowered = text.strip().lower()

    for tag, keywords in keyword_map.items():
        for kw in keywords:
            if kw.lower() in lowered:
                scores[tag] += 1
    return scores


def _pick_best_tag(
    scores: Dict[str, int],
    default_tag: str,
    priority_order: List[str] | None = None,
) -> str:
    if not scores:
        return default_tag

    max_score = max(scores.values())
    if max_score <= 0:
        return default_tag

    candidates = [tag for tag, score in scores.items() if score == max_score]

    if len(candidates) == 1:
        return candidates[0]

    if priority_order:
        for tag in priority_order:
            if tag in candidates:
                return tag

    return candidates[0]


def classify_text(raw_text: str) -> Dict[str, str]:
    """
    진단 문장/응답 텍스트를 받아 내부 TAG 3개와 고객용 display tag 3개를 반환한다.
    """
    text = (raw_text or "").strip()

    type_scores = _score_text(text, TYPE_KEYWORDS)
    module_scores = _score_text(text, MODULE_KEYWORDS)
    framework_scores = _score_text(text, FRAMEWORK_KEYWORDS)

    type_primary = _pick_best_tag(
        type_scores,
        default_tag=DEFAULT_TYPE,
        priority_order=["Type_NoEnergy", "Type_NoCompass", "Type_NoAction"],
    )
    module_primary = _pick_best_tag(
        module_scores,
        default_tag=DEFAULT_MODULE,
    )
    framework_stage = _pick_best_tag(
        framework_scores,
        default_tag=DEFAULT_FRAMEWORK,
        priority_order=[
            "Framework_Recovery",
            "Framework_Awareness",
            "Framework_SkillTraining",
            "Framework_Optimization",
            "Framework_Legacy",
        ],
    )

    display_tags = generate_display_tags(
        type_primary=type_primary,
        module_primary=module_primary,
        framework_stage=framework_stage,
    )

    return {
        "type_primary": type_primary,
        "module_primary": module_primary,
        "framework_stage": framework_stage,
        "display_tag_1": display_tags[0] if len(display_tags) > 0 else "",
        "display_tag_2": display_tags[1] if len(display_tags) > 1 else "",
        "display_tag_3": display_tags[2] if len(display_tags) > 2 else "",
    }


def validate_tag_result(tag_result: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    분류 결과가 정의된 내부 TAG 체계 안에 있는지 검증한다.
    """
    errors: List[str] = []

    type_primary = tag_result.get("type_primary", "")
    module_primary = tag_result.get("module_primary", "")
    framework_stage = tag_result.get("framework_stage", "")

    if type_primary not in TYPE_TAGS:
        errors.append(f"invalid type_primary: {type_primary}")

    if module_primary not in MODULE_TAGS:
        errors.append(f"invalid module_primary: {module_primary}")

    if framework_stage not in FRAMEWORK_TAGS:
        errors.append(f"invalid framework_stage: {framework_stage}")

    return (len(errors) == 0, errors)