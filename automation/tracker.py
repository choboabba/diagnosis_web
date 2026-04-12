# -*- coding: utf-8 -*-
"""
automation/tracker.py

이 파일은 자동화 처리 과정에서 사용하는 상태값(status)과
처리 여부(processed), 처리 시각(processed_at), 마지막 행동 시각(last_action_at) 등을
일관되게 관리하기 위한 보조 모듈입니다.

이 파일에서 하는 일
1. 자동화 단계별 status 값을 정리합니다.
2. 처리 완료용 공통 업데이트 값을 만듭니다.
3. 오류 기록용 공통 업데이트 값을 만듭니다.
4. 나중에 clicked / purchased 추적 로직을 확장할 수 있는 기반을 제공합니다.

왜 이 파일이 필요한가?
- 지금은 main.py 안에서 직접 status를 넣어도 동작합니다.
- 하지만 단계가 늘어나면 상태 관리 로직이 여러 파일에 흩어집니다.
- tracker.py로 분리해두면 이후 유지보수와 확장이 쉬워집니다.

주의
- 현재는 "기본 추적 구조"만 구현합니다.
- 클릭(clicked) / 구매(purchased) 자동 추적은 아직 외부 이벤트 연동 전이라
  기본값 유지 수준으로만 사용합니다.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from automation import config


class Tracker:
    """
    자동화 상태 추적용 보조 클래스입니다.

    이 클래스는 직접 Google Sheets를 건드리지는 않고,
    "업데이트할 값 묶음"을 만들어서 main.py 또는 sheets_client.py가 사용하도록 돕습니다.
    """

    def __init__(self) -> None:
        """
        현재 단계에서는 별도 초기화 상태값이 필요 없습니다.
        """
        pass

    # ------------------------------------------------------------
    # 1. 현재 시각 문자열 생성
    # ------------------------------------------------------------
    def now_str(self) -> str:
        """
        현재 시각을 문자열 형태로 반환합니다.

        형식 예시
        2026-04-12 21:45:30
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------
    # 2. 처리 성공용 공통 업데이트 생성
    # ------------------------------------------------------------
    def build_success_updates(
        self,
        status: str = "drafted",
        processed: str = "Y",
        include_last_action_at: bool = True,
        extra_updates: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        처리 성공 시 공통으로 시트에 기록할 값들을 만듭니다.

        매개변수
        - status:
          현재 단계 상태값
          예: tagged, routed, drafted
        - processed:
          처리 완료 여부
          기본값은 "Y"
        - include_last_action_at:
          last_action_at도 현재 시각으로 넣을지 여부
        - extra_updates:
          추가로 합칠 값이 있으면 딕셔너리로 전달

        반환 예시
        {
            "status": "drafted",
            "processed": "Y",
            "processed_at": "2026-04-12 21:45:30",
            "last_action_at": "2026-04-12 21:45:30",
            "error_message": ""
        }
        """
        now = self.now_str()

        updates: Dict[str, Any] = {
            config.COL_STATUS: status,
            config.COL_PROCESSED: processed,
            config.COL_PROCESSED_AT: now,
            config.COL_ERROR_MESSAGE: "",
        }

        if include_last_action_at:
            updates[config.COL_LAST_ACTION_AT] = now

        if extra_updates:
            updates.update(extra_updates)

        return updates

    # ------------------------------------------------------------
    # 3. 오류 기록용 공통 업데이트 생성
    # ------------------------------------------------------------
    def build_error_updates(
        self,
        error_message: str,
        processed: str = "N",
        include_last_action_at: bool = False,
        extra_updates: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        오류 발생 시 공통으로 시트에 기록할 값들을 만듭니다.

        매개변수
        - error_message:
          오류 내용 문자열
        - processed:
          오류가 났으므로 기본값은 "N"
        - include_last_action_at:
          오류 발생도 마지막 행동으로 기록할지 여부
        - extra_updates:
          추가 업데이트 값

        반환 예시
        {
            "status": "error",
            "processed": "N",
            "error_message": "..."
        }
        """
        updates: Dict[str, Any] = {
            config.COL_STATUS: config.ERROR_STATUS,
            config.COL_PROCESSED: processed,
            config.COL_ERROR_MESSAGE: error_message,
        }

        if include_last_action_at:
            updates[config.COL_LAST_ACTION_AT] = self.now_str()

        if extra_updates:
            updates.update(extra_updates)

        return updates

    # ------------------------------------------------------------
    # 4. 초기 추적값 생성
    # ------------------------------------------------------------
    def build_initial_tracking_values(self) -> Dict[str, Any]:
        """
        신규 리드 또는 최초 자동화 단계에서 사용할 기본 추적값 묶음을 생성합니다.

        현재 기준 기본값
        - clicked = N
        - clicked_count = 0
        - purchased = N

        나중에 확장 가능
        - clicked_last_link
        - clicked_last_at
        - purchased_product
        - purchase_amount
        """
        return {
            config.COL_CLICKED: config.DEFAULT_CLICKED_VALUE,
            config.COL_CLICKED_COUNT: config.DEFAULT_CLICKED_COUNT,
            config.COL_PURCHASED: config.DEFAULT_PURCHASED_VALUE,
        }

    # ------------------------------------------------------------
    # 5. 클릭 발생 시 업데이트 값 생성 - 확장용
    # ------------------------------------------------------------
    def build_click_updates(
        self,
        clicked_last_link: str,
        clicked_count: int,
    ) -> Dict[str, Any]:
        """
        나중에 클릭 로그 연동 시 사용할 확장용 함수입니다.

        현재 단계에서는 실제 자동 호출하지 않지만,
        구조를 미리 만들어 둡니다.
        """
        now = self.now_str()

        return {
            config.COL_CLICKED: "Y",
            config.COL_CLICKED_COUNT: clicked_count,
            config.COL_CLICKED_LAST_LINK: clicked_last_link,
            config.COL_CLICKED_LAST_AT: now,
            config.COL_LAST_ACTION_AT: now,
        }

    # ------------------------------------------------------------
    # 6. 구매 발생 시 업데이트 값 생성 - 확장용
    # ------------------------------------------------------------
    def build_purchase_updates(
        self,
        purchased_product: str,
        purchase_amount: Any,
    ) -> Dict[str, Any]:
        """
        나중에 구매 로그 연동 시 사용할 확장용 함수입니다.

        현재 단계에서는 실제 자동 호출하지 않지만,
        구조를 미리 만들어 둡니다.
        """
        now = self.now_str()

        return {
            config.COL_PURCHASED: "Y",
            config.COL_PURCHASED_PRODUCT: purchased_product,
            config.COL_PURCHASE_AMOUNT: purchase_amount,
            config.COL_LAST_ACTION_AT: now,
        }


# ------------------------------------------------------------
# 7. 단독 실행 테스트용
# ------------------------------------------------------------
if __name__ == "__main__":
    tracker = Tracker()

    print("=" * 60)
    print("Tracker 테스트 - 성공 업데이트")
    print("=" * 60)
    success_updates = tracker.build_success_updates(status="drafted")
    for key, value in success_updates.items():
        print(f"{key}: {value}")

    print("-" * 60)
    print("Tracker 테스트 - 오류 업데이트")
    print("-" * 60)
    error_updates = tracker.build_error_updates(error_message="테스트 오류")
    for key, value in error_updates.items():
        print(f"{key}: {value}")