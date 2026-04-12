# -*- coding: utf-8 -*-
"""
automation/email_builder.py

이 파일은 email_template_id와 추천값들을 이용해서
이메일 제목 초안과 본문 초안을 생성하는 역할을 담당합니다.

이 파일에서 하는 일
1. templates 폴더의 템플릿 파일을 읽습니다.
2. [SUBJECT] / [BODY] 구역을 분리합니다.
3. {{name}}, {{recommended_guide}}, {{recommended_magazine}},
   {{recommended_product}}, {{cta_link}} 같은 치환 변수를 실제 값으로 바꿉니다.
4. 최종적으로 시트에 저장할 제목 초안 / 본문 초안을 반환합니다.

왜 이 파일이 필요한가?
- content_map에서 email_template_id를 찾아도,
  실제 문장으로 바꿔주는 단계가 따로 필요합니다.
- 템플릿 파일을 유지하면 나중에 이메일 문구를 코드 수정 없이 바꿀 수 있습니다.

주의
- 현재는 템플릿 기반 생성입니다.
- 아직 Ollama/Gemma는 사용하지 않습니다.
- 실제 URL이 없으므로 cta_link는 config.DEFAULT_CTA_LINK를 사용합니다.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

from automation import config


class EmailBuilder:
    """
    이메일 템플릿을 읽어 제목/본문 초안을 만드는 클래스입니다.
    """

    def __init__(self) -> None:
        """
        초기화 시점에는 별도 상태를 많이 저장하지 않습니다.
        필요할 때마다 템플릿 파일을 읽는 구조입니다.
        """
        pass

    # ------------------------------------------------------------
    # 1. 외부에서 사용하는 메인 함수
    # ------------------------------------------------------------
    def build_email_draft(
        self,
        email_template_id: str,
        row: Dict[str, str],
        routed_data: Dict[str, str],
        cta_link: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        이메일 초안을 생성합니다.

        입력값
        - email_template_id:
          예: email_result_a
        - row:
          Google Sheets의 원본 리드 데이터 1행
        - routed_data:
          content_router.py가 반환한 추천값 딕셔너리
        - cta_link:
          실제 CTA 링크가 있으면 사용하고,
          없으면 config.DEFAULT_CTA_LINK 사용

        반환값
        {
            "email_subject_draft": "...",
            "email_body_draft": "..."
        }
        """
        template_path = self._get_template_path(email_template_id)
        template_text = self._read_template_file(template_path)

        subject_template, body_template = self._split_template(template_text)

        replacements = self._build_replacements(
            row=row,
            routed_data=routed_data,
            cta_link=cta_link or config.DEFAULT_CTA_LINK,
        )

        subject = self._replace_variables(subject_template, replacements)
        body = self._replace_variables(body_template, replacements)

        return {
            config.COL_EMAIL_SUBJECT_DRAFT: subject.strip(),
            config.COL_EMAIL_BODY_DRAFT: body.strip(),
        }

    # ------------------------------------------------------------
    # 2. 템플릿 경로 찾기
    # ------------------------------------------------------------
    def _get_template_path(self, email_template_id: str) -> Path:
        """
        email_template_id를 실제 템플릿 파일 경로로 변환합니다.

        예:
        email_result_a -> templates/email_result_a.txt
        """
        template_path = config.EMAIL_TEMPLATE_FILES.get(email_template_id)

        if template_path is None:
            raise KeyError(
                f"정의되지 않은 email_template_id 입니다: {email_template_id}"
            )

        if not template_path.exists():
            raise FileNotFoundError(
                f"이메일 템플릿 파일이 없습니다: {template_path}"
            )

        return template_path

    # ------------------------------------------------------------
    # 3. 템플릿 파일 읽기
    # ------------------------------------------------------------
    def _read_template_file(self, template_path: Path) -> str:
        """
        템플릿 txt 파일 전체 내용을 문자열로 읽어 반환합니다.
        """
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    # ------------------------------------------------------------
    # 4. SUBJECT / BODY 구역 분리
    # ------------------------------------------------------------
    def _split_template(self, template_text: str) -> Tuple[str, str]:
        """
        템플릿 텍스트에서 [SUBJECT], [BODY] 구역을 분리합니다.

        템플릿 예시
        [SUBJECT]
        제목 문장

        [BODY]
        본문 문장
        """
        subject_marker = "[SUBJECT]"
        body_marker = "[BODY]"

        if subject_marker not in template_text or body_marker not in template_text:
            raise ValueError(
                "템플릿 형식이 올바르지 않습니다. [SUBJECT]와 [BODY]가 모두 필요합니다."
            )

        subject_start = template_text.index(subject_marker) + len(subject_marker)
        body_start = template_text.index(body_marker)

        subject_text = template_text[subject_start:body_start].strip()
        body_text = template_text[body_start + len(body_marker):].strip()

        return subject_text, body_text

    # ------------------------------------------------------------
    # 5. 치환 변수 딕셔너리 만들기
    # ------------------------------------------------------------
    def _build_replacements(
        self,
        row: Dict[str, str],
        routed_data: Dict[str, str],
        cta_link: str,
    ) -> Dict[str, str]:
        """
        템플릿 안의 {{변수명}}을 실제 값으로 바꾸기 위한 딕셔너리를 생성합니다.
        """
        name = str(row.get(config.COL_NAME, "")).strip()
        if not name:
            name = "고객"

        replacements = {
            "{{name}}": name,
            "{{recommended_guide}}": str(
                routed_data.get(config.COL_RECOMMENDED_GUIDE, "")
            ).strip(),
            "{{recommended_magazine}}": str(
                routed_data.get(config.COL_RECOMMENDED_MAGAZINE, "")
            ).strip(),
            "{{recommended_product}}": str(
                routed_data.get(config.COL_RECOMMENDED_PRODUCT, "")
            ).strip(),
            "{{cta_link}}": cta_link,
        }

        return replacements

    # ------------------------------------------------------------
    # 6. 실제 치환 수행
    # ------------------------------------------------------------
    def _replace_variables(
        self,
        text: str,
        replacements: Dict[str, str],
    ) -> str:
        """
        텍스트 안의 치환 변수를 실제 값으로 바꿉니다.
        """
        result = text

        for key, value in replacements.items():
            result = result.replace(key, value)

        return result


# ------------------------------------------------------------
# 7. 단독 실행 테스트용
# ------------------------------------------------------------
if __name__ == "__main__":
    builder = EmailBuilder()

    sample_row = {
        "name": "홍길동",
    }

    sample_routed_data = {
        "recommended_magazine": "magazine_emotion_01",
        "recommended_guide": "guide_emotion_02",
        "recommended_product": "product_coaching_01",
        "email_template_id": "email_result_a",
    }

    result = builder.build_email_draft(
        email_template_id="email_result_a",
        row=sample_row,
        routed_data=sample_routed_data,
    )

    print("=" * 60)
    print("이메일 초안 생성 테스트 결과")
    print("=" * 60)
    for key, value in result.items():
        print(f"[{key}]")
        print(value)
        print("-" * 60)