# automation/tag_definitions.py

from typing import List, Dict


# =========================================================
# 1) INTERNAL TAGS - 관리자/시스템 전용
# =========================================================

STAGE_TAGS: Dict[str, str] = {
    "Stage_Visitor": "유입만 됨",
    "Stage_Lead": "이메일/연락처 확보 완료",
    "Stage_DiagnosisCompleted": "진단 완료",
    "Stage_FreeResourceUser": "무료 자료 수령",
    "Stage_LowTicketBuyer": "저가 상품 구매",
    "Stage_CoreBuyer": "핵심 상품 구매",
    "Stage_HighTicketBuyer": "고가 상품 구매",
    "Stage_RepeatBuyer": "재구매 고객",
}

SOURCE_TAGS: Dict[str, str] = {
    "Source_Instagram": "인스타그램",
    "Source_Reels": "릴스",
    "Source_Carousel": "캐러셀",
    "Source_ProfileLink": "프로필 링크",
    "Source_DM": "DM",
    "Source_Email": "이메일",
    "Source_Referral": "소개/추천",
}

INTEREST_TAGS: Dict[str, str] = {
    "Interest_NoEnergy": "에너지 문제 관심",
    "Interest_NoCompass": "기준/방향 문제 관심",
    "Interest_NoAction": "실행 문제 관심",
    "Interest_Recovery": "회복",
    "Interest_ParentingBasics": "기초육아정보",
    "Interest_Communication": "대화법",
    "Interest_Relationship": "관계",
    "Interest_Decluttering": "정리정돈",
    "Interest_Finance": "재정",
}

TYPE_TAGS: Dict[str, str] = {
    "Type_NoEnergy": "에너지의 부재",
    "Type_NoCompass": "기준의 부재",
    "Type_NoAction": "실천의 부재",
    "Type_NoEnergy_NoAction": "에너지+실천 복합형",
    "Type_NoCompass_NoEnergy": "기준+에너지 복합형",
    "Type_NoAction_NoCompass": "실천+기준 복합형",
    "Type_GlobalOverload": "전반 과부하",
}

MODULE_TAGS: Dict[str, str] = {
    "Module_ReviewJournal": "복기일기",
    "Module_TimeReuse": "시간재활용",
    "Module_MentalCare": "멘탈관리",
    "Module_PhysicalCare": "신체관리",
    "Module_FamilyIdentity": "가족정체성",
    "Module_ParentingBasics": "기초육아정보",
    "Module_Communication": "대화법",
    "Module_RelationshipRecovery": "관계회복",
    "Module_Setup": "정리정돈(환경셋)",
    "Module_FinanceManagement": "재정관리",
}

FRAMEWORK_TAGS: Dict[str, str] = {
    "Framework_Awareness": "인식",
    "Framework_Recovery": "회복",
    "Framework_SkillTraining": "기술습득훈련",
    "Framework_Optimization": "최적화내면화",
    "Framework_Legacy": "대물림",
}

PRODUCT_TAGS: Dict[str, str] = {
    "Product_Magazine": "매거진",
    "Product_Guidebook": "가이드북",
    "Product_Workbook": "워크북",
    "Product_Template": "템플릿",
    "Product_Challenge": "챌린지",
    "Product_OnlineVOD": "온라인 VOD",
    "Product_GroupCoaching": "그룹 코칭",
    "Product_Masterclass": "마스터클래스",
    "Product_1on1Coaching": "1:1 코칭",
}

FOLLOWUP_TAGS: Dict[str, str] = {
    "FollowUp_WelcomeSent": "웰컴 발송 완료",
    "FollowUp_DiagnosisResultSent": "진단 결과 발송 완료",
    "FollowUp_ReviewRequested": "후기 요청 완료",
    "FollowUp_ReviewCompleted": "후기 작성 완료",
    "FollowUp_UpsellReady": "업셀 가능 상태",
    "FollowUp_ReengagementNeeded": "재활성화 필요",
    "FollowUp_Inactive30D": "30일 비활성",
}


# =========================================================
# 2) DISPLAY TAGS - 고객 노출용 한국어 TAG
# =========================================================

DISPLAY_TAG_MAP: Dict[str, str] = {
    # 3No
    "Type_NoEnergy": "#에너지회복",
    "Type_NoCompass": "#방향설정",
    "Type_NoAction": "#실행루틴",

    # 10 Modules
    "Module_ReviewJournal": "#복기습관",
    "Module_TimeReuse": "#시간관리",
    "Module_MentalCare": "#감정관리",
    "Module_PhysicalCare": "#체력관리",
    "Module_FamilyIdentity": "#가족기준",
    "Module_ParentingBasics": "#육아기초",
    "Module_Communication": "#대화법",
    "Module_RelationshipRecovery": "#관계회복",
    "Module_Setup": "#정리정돈",
    "Module_FinanceManagement": "#재정관리",

    # Framework
    "Framework_Awareness": "#문제이해",
    "Framework_Recovery": "#회복단계",
    "Framework_SkillTraining": "#실행연습",
    "Framework_Optimization": "#습관정착",
    "Framework_Legacy": "#가족시스템",
}


# =========================================================
# 3) 올해 운영 대상 상품
# =========================================================

ACTIVE_PRODUCTS_2026: List[str] = [
    "Product_Magazine",
    "Product_Guidebook",
    "Product_Workbook",
    "Product_Challenge",
]


# =========================================================
# 4) 유틸 함수
# =========================================================

def generate_display_tags(
    type_primary: str,
    module_primary: str,
    framework_stage: str,
) -> List[str]:
    """
    고객에게 노출할 한국어 TAG 3개 생성
    우선순위:
    1) Type
    2) Module
    3) Framework
    """
    candidates = [
        DISPLAY_TAG_MAP.get(type_primary, ""),
        DISPLAY_TAG_MAP.get(module_primary, ""),
        DISPLAY_TAG_MAP.get(framework_stage, ""),
    ]
    return [tag for tag in candidates if tag]


def is_active_product(product_code: str) -> bool:
    """
    올해 운영 대상 상품인지 여부 확인
    """
    return product_code in ACTIVE_PRODUCTS_2026