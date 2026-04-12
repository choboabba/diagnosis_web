# -*- coding: utf-8 -*-
"""
automation/content_router.py

이 파일은 TAG 결과를 바탕으로
어떤 매거진 / 가이드 / 상품 / 이메일 템플릿을 연결할지 결정하는 역할을 담당합니다.

이 파일에서 하는 일
1. data/content_map.csv 파일을 읽습니다.
2. tag_parent_type, tag_interest, tag_urgency 값을 기준으로
   일치하는 매핑 행을 찾습니다.
3. 찾은 결과에서 추천 매거진 / 가이드 / 상품 / 이메일 템플릿 ID를 반환합니다.
4. 일치하는 행이 없으면 기본값을 반환합니다.

왜 이 파일이 필요한가?
- TAG를 만들었다고 끝이 아니라,
  그 TAG에 맞는 실제 콘텐츠 연결값을 찾아야 자동화가 완성됩니다.
- 이후 이메일 초안 생성에서도 email_template_id가 필요합니다.
- 나중에 content_map.csv만 바꿔도 추천 흐름을 쉽게 수정할 수 있습니다.

주의
- 이 파일은 룰 기반 매핑입니다.
- 아직 실제 URL은 쓰지 않고 ID 기준으로 연결합니다.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from automation import config


class ContentRouter:
    """
    content_map.csv를 읽어서
    TAG 조합에 맞는 추천 콘텐츠를 찾아주는 클래스입니다.
    """

    def __init__(self, content_map_file: Optional[Path] = None) -> None:
        """
        ContentRouter 초기화

        매개변수
        - content_map_file:
          content_map.csv 경로를 직접 지정하고 싶을 때 사용합니다.
          지정하지 않으면 config.CONTENT_MAP_FILE 값을 사용합니다.
        """
        self.content_map_file = content_map_file or config.CONTENT_MAP_FILE
        self.rows = self._load_content_map()

    # ------------------------------------------------------------
    # 1. CSV 로드
    # ------------------------------------------------------------
    def _load_content_map(self) -> List[Dict[str, str]]:
        """
        content_map.csv 파일을 읽어서
        각 행을 딕셔너리 리스트 형태로 반환합니다.

        반환 예시
        [
            {
                "tag_parent_type": "ptype_anxiety",
                "tag_interest": "interest_emotion",
                "tag_urgency": "urgency_high",
                "recommended_magazine": "magazine_emotion_01",
                "recommended_guide": "guide_emotion_02",
                "recommended_product": "product_coaching_01",
                "email_template_id": "email_result_a"
            },
            ...
        ]
        """
        if not self.content_map_file.exists():
            raise FileNotFoundError(
                f"content_map.csv 파일이 없습니다: {self.content_map_file}"
            )

        rows: List[Dict[str, str]] = []

        with open(self.content_map_file, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                cleaned_row = {
                    key.strip(): value.strip()
                    for key, value in row.items()
                    if key is not None
                }
                rows.append(cleaned_row)

        return rows

    # ------------------------------------------------------------
    # 2. TAG 기준 추천값 찾기
    # ------------------------------------------------------------
    def route_by_tags(
        self,
        tag_parent_type: str,
        tag_interest: str,
        tag_urgency: str,
    ) -> Dict[str, str]:
        """
        TAG 3개를 기준으로 content_map.csv에서 일치하는 행을 찾습니다.

        일치 조건
        - tag_parent_type
        - tag_interest
        - tag_urgency

        반환값
        {
            "recommended_magazine": "...",
            "recommended_guide": "...",
            "recommended_product": "...",
            "email_template_id": "..."
        }

        일치하는 행이 없으면 기본값 반환
        """
        for row in self.rows:
            if (
                row.get("tag_parent_type") == tag_parent_type
                and row.get("tag_interest") == tag_interest
                and row.get("tag_urgency") == tag_urgency
            ):
                return self._build_result(row)

        return self._default_result()

    # ------------------------------------------------------------
    # 3. row 딕셔너리에서 반환값 구조 만들기
    # ------------------------------------------------------------
    def _build_result(self, row: Dict[str, str]) -> Dict[str, str]:
        """
        content_map.csv의 1개 행을
        자동화 코드에서 쓰기 좋은 출력 구조로 변환합니다.
        """
        return {
            config.COL_RECOMMENDED_MAGAZINE: row.get("recommended_magazine", ""),
            config.COL_RECOMMENDED_GUIDE: row.get("recommended_guide", ""),
            config.COL_RECOMMENDED_PRODUCT: row.get("recommended_product", ""),
            config.COL_EMAIL_TEMPLATE_ID: row.get("email_template_id", ""),
        }

    # ------------------------------------------------------------
    # 4. 기본 반환값
    # ------------------------------------------------------------
    def _default_result(self) -> Dict[str, str]:
        """
        content_map.csv에서 일치하는 행을 찾지 못했을 때 반환할 기본값입니다.

        현재는 default 계열 ID를 반환합니다.
        나중에 실제 운영 구조가 정리되면 이 기본값도 바꿀 수 있습니다.
        """
        return {
            config.COL_RECOMMENDED_MAGAZINE: "magazine_default_01",
            config.COL_RECOMMENDED_GUIDE: "guide_default_01",
            config.COL_RECOMMENDED_PRODUCT: "product_default_01",
            config.COL_EMAIL_TEMPLATE_ID: "email_result_c",
        }


# ------------------------------------------------------------
# 5. 단독 실행 테스트용
# ------------------------------------------------------------
if __name__ == "__main__":
    router = ContentRouter()

    result = router.route_by_tags(
        tag_parent_type="ptype_anxiety",
        tag_interest="interest_emotion",
        tag_urgency="urgency_high",
    )

    print("=" * 60)
    print("content_map 매칭 테스트 결과")
    print("=" * 60)
    for key, value in result.items():
        print(f"{key}: {value}")