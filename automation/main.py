# -*- coding: utf-8 -*-
"""
automation/main.py

이 파일은 지금까지 만든 자동화 모듈들을 실제로 한 번에 연결하는 실행 파일입니다.

이 파일에서 하는 일
1. Google Sheets에 연결합니다.
2. 미처리 리드를 찾습니다.
3. 각 리드에 대해 TAG를 생성합니다.
4. TAG 결과를 기준으로 content_map을 매칭합니다.
5. 이메일 초안을 생성합니다.
6. tracker.py를 사용해 처리 상태값을 일관되게 구성합니다.
7. 생성된 결과를 다시 Google Sheets에 저장합니다.
8. 오류 발생 시 tracker.py 기반 오류 상태값을 기록합니다.

지금 단계의 목적
- 지금까지 만든 모듈들을 실제 자동화 흐름으로 묶기
- 상태 관리 로직을 tracker.py로 분리해서 유지보수성을 높이기

주의
- 지금은 1차 자동화입니다.
- 실제 메일 발송은 하지 않습니다.
- 시트에 TAG / 추천값 / 이메일 초안만 기록합니다.
"""

from __future__ import annotations

from typing import Dict, Any

from automation import config
from automation.sheets_client import SheetsClient
from automation.tag_engine import TagEngine
from automation.content_router import ContentRouter
from automation.email_builder import EmailBuilder
from automation.tracker import Tracker


def build_final_updates(
    tag_data: Dict[str, Any],
    routed_data: Dict[str, Any],
    email_data: Dict[str, Any],
    tracking_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    각 단계에서 생성한 결과를 하나의 업데이트 딕셔너리로 합칩니다.

    합치는 대상
    - TAG 생성 결과
    - content_map 매칭 결과
    - 이메일 초안 결과
    - tracker 기반 상태/처리 정보
    """
    updates: Dict[str, Any] = {}

    updates.update(tag_data)
    updates.update(routed_data)
    updates.update(email_data)
    updates.update(tracking_data)

    return updates


def process_one_row(
    client: SheetsClient,
    tag_engine: TagEngine,
    router: ContentRouter,
    email_builder: EmailBuilder,
    tracker: Tracker,
    row: Dict[str, Any],
) -> None:
    """
    미처리 리드 1건을 실제로 처리합니다.

    처리 순서
    1. TAG 생성
    2. content_map 매칭
    3. 이메일 초안 생성
    4. tracker를 이용해 상태값 생성
    5. 시트 업데이트
    """
    row_number = row["row_number"]

    # 1. TAG 생성
    tag_data = tag_engine.build_tags_from_row(row)

    # 2. content_map 매칭
    routed_data = router.route_by_tags(
        tag_parent_type=tag_data[config.COL_TAG_PARENT_TYPE],
        tag_interest=tag_data[config.COL_TAG_INTEREST],
        tag_urgency=tag_data[config.COL_TAG_URGENCY],
    )

    # 3. 이메일 초안 생성
    email_data = email_builder.build_email_draft(
        email_template_id=routed_data[config.COL_EMAIL_TEMPLATE_ID],
        row=row,
        routed_data=routed_data,
    )

    # 4. 처리 성공 상태값 생성
    tracking_data = tracker.build_success_updates(status="drafted")

    # 5. 최종 업데이트 데이터 조합
    final_updates = build_final_updates(
        tag_data=tag_data,
        routed_data=routed_data,
        email_data=email_data,
        tracking_data=tracking_data,
    )

    # 6. 실제 시트 업데이트
    client.update_row_by_row_number(
        row_number=row_number,
        updates=final_updates,
    )


def main() -> None:
    """
    자동화 메인 실행 함수입니다.
    """
    # 1. 공통 객체 생성
    client = SheetsClient()
    tag_engine = TagEngine()
    router = ContentRouter()
    email_builder = EmailBuilder()
    tracker = Tracker()

    # 2. Sheets 연결
    client.connect()

    # 3. 필수 컬럼 검사
    is_valid, missing_columns = client.validate_required_columns()
    if not is_valid:
        raise ValueError(
            f"시트 필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}"
        )

    # 4. 미처리 리드 조회
    unprocessed_rows = client.get_unprocessed_leads()

    print("=" * 60)
    print("자동화 실행 시작")
    print("=" * 60)
    print(f"미처리 리드 수: {len(unprocessed_rows)}")

    # 5. 미처리 리드가 없으면 종료
    if not unprocessed_rows:
        print("처리할 신규 리드가 없습니다.")
        return

    # 6. 각 리드를 순회하며 처리
    success_count = 0
    error_count = 0

    for row in unprocessed_rows:
        row_number = row.get("row_number")

        try:
            process_one_row(
                client=client,
                tag_engine=tag_engine,
                router=router,
                email_builder=email_builder,
                tracker=tracker,
                row=row,
            )
            success_count += 1
            print(f"[성공] row_number={row_number}")

        except Exception as exc:
            error_count += 1
            error_message = str(exc)

            # tracker를 이용해 오류 상태값 생성
            error_updates = tracker.build_error_updates(
                error_message=error_message,
                processed="N",
            )

            # 오류 내용을 시트에 기록
            client.update_row_by_row_number(
                row_number=row_number,
                updates=error_updates,
            )

            print(f"[오류] row_number={row_number} / {error_message}")

    # 7. 실행 결과 요약 출력
    print("-" * 60)
    print("자동화 실행 종료")
    print(f"성공: {success_count}")
    print(f"오류: {error_count}")


if __name__ == "__main__":
    main()