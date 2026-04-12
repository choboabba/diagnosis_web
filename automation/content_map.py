# automation/content_map.py

from typing import Dict, List


# =========================================================
# 기본 상품 구조 (올해 기준)
# =========================================================

DEFAULT_PRODUCT_FLOW: List[str] = [
    "Product_Magazine",
    "Product_Guidebook",
    "Product_Challenge",
]


# =========================================================
# 모듈별 전자책/챌린지 매핑
# =========================================================

MODULE_PRODUCT_MAP: Dict[str, Dict[str, str]] = {

    "Module_MentalCare": {
        "guide": "감정회복 가이드북",
        "challenge": "감정회복 챌린지",
    },

    "Module_Communication": {
        "guide": "대화법 가이드북",
        "challenge": "대화법 챌린지",
    },

    "Module_TimeReuse": {
        "guide": "시간관리 워크북",
        "challenge": "시간관리 챌린지",
    },

    "Module_ReviewJournal": {
        "guide": "복기일기 워크북",
        "challenge": "복기습관 챌린지",
    },

    "Module_RelationshipRecovery": {
        "guide": "관계회복 가이드북",
        "challenge": "관계회복 챌린지",
    },

    "Module_FamilyIdentity": {
        "guide": "가족정체성 워크북",
        "challenge": "가족정체성 챌린지",
    },

    "Module_ParentingBasics": {
        "guide": "육아기초 가이드북",
        "challenge": "육아기초 챌린지",
    },

    "Module_Setup": {
        "guide": "정리정돈 가이드북",
        "challenge": "정리정돈 챌린지",
    },

    "Module_FinanceManagement": {
        "guide": "재정관리 워크북",
        "challenge": "재정관리 챌린지",
    },

    "Module_PhysicalCare": {
        "guide": "체력관리 가이드북",
        "challenge": "체력회복 챌린지",
    },
}


# =========================================================
# 추천 로직
# =========================================================

def get_recommended_products(tag_result: Dict[str, str]) -> Dict[str, str]:
    """
    tag_engine 결과를 받아
    추천 상품 3개를 반환
    """

    module = tag_result.get("module_primary", "")

    module_config = MODULE_PRODUCT_MAP.get(module, None)

    # fallback
    if not module_config:
        return {
            "product_1": "매거진",
            "product_2": "기본 가이드북",
            "product_3": "기본 챌린지",
        }

    return {
        "product_1": "매거진",
        "product_2": module_config["guide"],
        "product_3": module_config["challenge"],
    }