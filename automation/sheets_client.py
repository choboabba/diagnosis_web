# -*- coding: utf-8 -*-
"""
automation/sheets_client.py

이 파일은 Google Sheets와 직접 통신하는 역할을 담당합니다.

이 파일에서 하는 일
1. 서비스 계정 키 파일로 Google Sheets에 인증합니다.
2. 지정한 스프레드시트와 워크시트에 연결합니다.
3. 시트의 헤더(컬럼명)를 읽습니다.
4. 전체 행 데이터를 "딕셔너리 리스트" 형태로 가져옵니다.
5. 아직 처리되지 않은 리드만 골라냅니다.
6. 특정 행의 특정 컬럼값들을 업데이트합니다.
7. 필수 컬럼이 실제 시트에 모두 있는지 검사합니다.

왜 이 파일이 필요한가?
- Google Sheets 접근 로직을 다른 파일에 흩어 놓으면 유지보수가 어렵습니다.
- 추후 Sheets 대신 다른 저장소(DB)로 바꾸더라도 이 파일만 교체하면 됩니다.
- 자동화의 입구와 출구를 한 곳에서 관리할 수 있습니다.

주의
- 이 코드는 gspread 라이브러리를 사용합니다.
- 실행 전 아래 패키지가 설치되어 있어야 합니다.

  pip install gspread google-auth

- service_account.json 파일이 secrets 폴더에 있어야 합니다.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import gspread
from gspread import Worksheet
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

from automation import config


class SheetsClient:
    """
    Google Sheets와 통신하는 전용 클래스입니다.

    이 클래스를 만드는 이유
    - 인증 / 연결 / 조회 / 업데이트를 객체 하나로 묶기 위함
    - 다른 파일에서 재사용하기 쉬움
    - 나중에 테스트할 때도 구조가 명확함
    """

    def __init__(self) -> None:
        """
        객체가 만들어질 때 기본 속성만 준비합니다.

        실제 연결은 connect() 호출 시점에 수행합니다.
        """
        self.gc: Optional[gspread.Client] = None
        self.spreadsheet = None
        self.worksheet: Optional[Worksheet] = None
        self.headers: List[str] = []

    # ------------------------------------------------------------
    # 1. Google Sheets 연결
    # ------------------------------------------------------------
    def connect(self) -> None:
        """
        서비스 계정 키 파일을 사용해 Google Sheets에 연결합니다.

        연결 순서
        1. config.py에 정의된 service_account.json 경로 확인
        2. gspread로 인증
        3. 스프레드시트 이름으로 문서 열기
        4. 워크시트 이름으로 탭 열기
        5. 헤더 읽기

        예외가 발생할 수 있는 경우
        - 서비스 계정 키 파일이 없음
        - 스프레드시트 이름이 틀림
        - 워크시트 이름이 틀림
        - 서비스 계정 이메일이 해당 시트에 공유되지 않음
        """
        # 필수 디렉터리가 없으면 자동 생성합니다.
        # 실제 서비스 계정 키 파일은 자동 생성되지 않으므로 따로 넣어야 합니다.
        config.ensure_directories()

        if not config.SERVICE_ACCOUNT_FILE.exists():
            raise FileNotFoundError(
                f"서비스 계정 키 파일이 없습니다: {config.SERVICE_ACCOUNT_FILE}"
            )

        # 서비스 계정 키 파일로 인증합니다.
        self.gc = gspread.service_account(filename=str(config.SERVICE_ACCOUNT_FILE))

        try:
            # 스프레드시트 파일명으로 문서를 엽니다.
            self.spreadsheet = self.gc.open(config.SPREADSHEET_NAME)
        except SpreadsheetNotFound as exc:
            raise SpreadsheetNotFound(
                f"스프레드시트를 찾을 수 없습니다. "
                f"SPREADSHEET_NAME 값을 확인하세요: {config.SPREADSHEET_NAME}"
            ) from exc

        try:
            # 문서 안에서 워크시트(탭) 이름으로 시트를 엽니다.
            self.worksheet = self.spreadsheet.worksheet(config.WORKSHEET_NAME)
        except WorksheetNotFound as exc:
            raise WorksheetNotFound(
                f"워크시트를 찾을 수 없습니다. "
                f"WORKSHEET_NAME 값을 확인하세요: {config.WORKSHEET_NAME}"
            ) from exc

        # 연결이 완료되면 헤더를 미리 읽어 둡니다.
        self.headers = self.get_headers()

    # ------------------------------------------------------------
    # 2. 헤더 읽기
    # ------------------------------------------------------------
    def get_headers(self) -> List[str]:
        """
        시트의 첫 번째 행을 읽어 헤더 목록을 반환합니다.

        반환 예시
        [
            "diagnosis_id",
            "created_at",
            "name",
            "email",
            ...
        ]
        """
        self._ensure_connected()

        # row_values(1)은 첫 번째 행 전체를 리스트로 가져옵니다.
        raw_headers = self.worksheet.row_values(1)

        # 앞뒤 공백 제거
        headers = [header.strip() for header in raw_headers if header.strip()]

        return headers

    # ------------------------------------------------------------
    # 3. 필수 컬럼 존재 여부 검사
    # ------------------------------------------------------------
    def validate_required_columns(self) -> Tuple[bool, List[str]]:
        """
        config.REQUIRED_COLUMNS에 정의된 필수 컬럼이
        실제 시트 헤더에 모두 존재하는지 검사합니다.

        반환값
        - (True, []) : 모두 존재
        - (False, ["누락컬럼1", "누락컬럼2"]) : 일부 누락
        """
        self._ensure_connected()

        current_headers = self.headers or self.get_headers()

        missing_columns = [
            column for column in config.REQUIRED_COLUMNS if column not in current_headers
        ]

        return len(missing_columns) == 0, missing_columns

    # ------------------------------------------------------------
    # 4. 전체 행 데이터 읽기
    # ------------------------------------------------------------
    def get_all_records(self) -> List[Dict[str, Any]]:
        """
        시트의 데이터를 "헤더 기준 딕셔너리 리스트"로 가져옵니다.

        gspread.get_all_records()는 첫 번째 행을 헤더로 사용하고,
        그 아래 데이터를 딕셔너리로 변환해 줍니다.

        반환 예시
        [
            {
                "diagnosis_id": "A001",
                "name": "홍길동",
                "email": "test@example.com",
                "processed": "N"
            },
            ...
        ]

        주의
        - 빈 셀은 보통 빈 문자열("")로 들어옵니다.
        - 숫자처럼 보여도 시트 상태에 따라 문자열로 들어올 수 있습니다.
        """
        self._ensure_connected()

        records = self.worksheet.get_all_records(
            expected_headers=self.headers,
            default_blank="",
            numericise_ignore=["all"],
        )

        return records

    # ------------------------------------------------------------
    # 5. 행 번호까지 포함한 전체 데이터 읽기
    # ------------------------------------------------------------
    def get_all_records_with_row_numbers(self) -> List[Dict[str, Any]]:
        """
        전체 레코드를 읽되, 실제 시트의 행 번호(row_number)도 함께 붙여 반환합니다.

        왜 필요한가?
        - Google Sheets 업데이트는 "몇 번째 행을 수정할지" 알아야 합니다.
        - get_all_records()만 쓰면 행 번호 정보가 없기 때문에 업데이트 시 불편합니다.

        시트 구조 기준
        - 1행: 헤더
        - 2행부터 실제 데이터

        따라서 records[0]은 실제 시트의 2행입니다.

        반환 예시
        [
            {
                "row_number": 2,
                "diagnosis_id": "A001",
                "name": "홍길동",
                ...
            },
            ...
        ]
        """
        records = self.get_all_records()

        records_with_row_numbers: List[Dict[str, Any]] = []

        for index, record in enumerate(records, start=2):
            item = {"row_number": index}
            item.update(record)
            records_with_row_numbers.append(item)

        return records_with_row_numbers

    # ------------------------------------------------------------
    # 6. 미처리 리드 찾기
    # ------------------------------------------------------------
    def get_unprocessed_leads(self) -> List[Dict[str, Any]]:
        """
        아직 처리되지 않은 리드만 골라 반환합니다.

        판단 기준
        - processed 컬럼 값이 "", "N", "n", None 중 하나이면 미처리로 간주

        반환값 예시
        [
            {
                "row_number": 2,
                "diagnosis_id": "A001",
                "name": "홍길동",
                "processed": "N",
                ...
            }
        ]
        """
        all_rows = self.get_all_records_with_row_numbers()

        unprocessed_rows: List[Dict[str, Any]] = []

        for row in all_rows:
            processed_value = row.get(config.COL_PROCESSED, "")

            if processed_value in config.UNPROCESSED_VALUES:
                unprocessed_rows.append(row)

        return unprocessed_rows

    # ------------------------------------------------------------
    # 7. 특정 행의 여러 컬럼 업데이트
    # ------------------------------------------------------------
    def update_row_by_row_number(self, row_number: int, updates: Dict[str, Any]) -> None:
        """
        실제 시트의 특정 행(row_number)에 대해,
        전달받은 컬럼들만 선택적으로 업데이트합니다.

        입력 예시
        row_number = 2
        updates = {
            "tag_parent_type": "ptype_anxiety",
            "status": "tagged",
            "processed": "Y"
        }

        동작 방식
        1. 헤더에서 컬럼 위치(몇 번째 열인지)를 찾음
        2. 해당 셀 주소를 계산
        3. 한 번에 batch_update 실행

        왜 batch_update를 쓰는가?
        - 셀 하나씩 업데이트하면 속도가 느립니다.
        - 한 행의 여러 값을 동시에 수정할 때 더 효율적입니다.
        """
        self._ensure_connected()

        if row_number < 2:
            raise ValueError("데이터 행 번호는 2 이상이어야 합니다. 1행은 헤더입니다.")

        if not updates:
            return

        # 최신 헤더를 다시 한 번 확보합니다.
        headers = self.headers or self.get_headers()

        # batch_update에 넣을 셀 목록을 준비합니다.
        cells_to_update = []

        for column_name, value in updates.items():
            if column_name not in headers:
                raise KeyError(
                    f"시트 헤더에 없는 컬럼입니다: {column_name}"
                )

            # 리스트 인덱스는 0부터 시작하지만, 시트 열 번호는 1부터 시작합니다.
            col_index = headers.index(column_name) + 1

            # gspread.utils.rowcol_to_a1 으로 A1 형식 주소를 만듭니다.
            cell_label = gspread.utils.rowcol_to_a1(row_number, col_index)

            cells_to_update.append(
                {
                    "range": cell_label,
                    "values": [[value]],
                }
            )

        # 시트에 한 번에 반영합니다.
        self.worksheet.batch_update(cells_to_update)

    # ------------------------------------------------------------
    # 8. 여러 행을 순회하며 업데이트할 때 사용할 보조 메서드
    # ------------------------------------------------------------
    def update_processed_success(
        self,
        row_number: int,
        status: str,
        processed: str = "Y",
        processed_at: str = "",
        error_message: str = "",
    ) -> None:
        """
        처리 성공 시 자주 쓰는 공통 업데이트를 묶은 보조 함수입니다.

        사용 예시
        - TAG 생성 후 상태 갱신
        - content_map 매칭 후 상태 갱신
        - 이메일 초안 생성 후 최종 처리 완료 표시
        """
        updates = {
            config.COL_STATUS: status,
            config.COL_PROCESSED: processed,
            config.COL_PROCESSED_AT: processed_at,
            config.COL_ERROR_MESSAGE: error_message,
        }

        self.update_row_by_row_number(row_number=row_number, updates=updates)

    # ------------------------------------------------------------
    # 9. 오류 상태 기록
    # ------------------------------------------------------------
    def update_error(
        self,
        row_number: int,
        error_message: str,
        processed: str = "N",
    ) -> None:
        """
        처리 중 오류가 발생했을 때 상태를 error로 기록합니다.

        왜 필요한가?
        - 어떤 행에서 왜 실패했는지 시트에서 바로 확인 가능
        - 자동화 디버깅이 쉬워짐
        """
        updates = {
            config.COL_STATUS: config.ERROR_STATUS,
            config.COL_PROCESSED: processed,
            config.COL_ERROR_MESSAGE: error_message,
        }

        self.update_row_by_row_number(row_number=row_number, updates=updates)

    # ------------------------------------------------------------
    # 10. 연결 상태 확인용 내부 메서드
    # ------------------------------------------------------------
    def _ensure_connected(self) -> None:
        """
        내부적으로 현재 객체가 Google Sheets에 연결되어 있는지 확인합니다.

        connect()를 호출하지 않고 다른 메서드를 먼저 실행하면
        명확한 오류 메시지를 주기 위해 사용합니다.
        """
        if self.gc is None or self.spreadsheet is None or self.worksheet is None:
            raise RuntimeError(
                "Google Sheets에 아직 연결되지 않았습니다. 먼저 connect()를 호출하세요."
            )


# ------------------------------------------------------------
# 11. 간단한 수동 테스트용 실행부
# ------------------------------------------------------------
# 이 파일을 단독 실행해서 연결 상태를 빠르게 점검할 수 있습니다.
if __name__ == "__main__":
    client = SheetsClient()
    client.connect()

    print("=" * 60)
    print("Google Sheets 연결 성공")
    print("=" * 60)

    print(f"스프레드시트 이름: {config.SPREADSHEET_NAME}")
    print(f"워크시트 이름: {config.WORKSHEET_NAME}")
    print(f"헤더 개수: {len(client.headers)}")
    print("헤더 목록:")
    for header in client.headers:
        print(f"- {header}")

    is_valid, missing = client.validate_required_columns()
    print("-" * 60)
    print(f"필수 컬럼 검사 결과: {is_valid}")
    if not is_valid:
        print("누락 컬럼:")
        for column in missing:
            print(f"- {column}")

    unprocessed = client.get_unprocessed_leads()
    print("-" * 60)
    print(f"미처리 리드 수: {len(unprocessed)}")

    if unprocessed:
        print("첫 번째 미처리 리드 예시:")
        first_row = unprocessed[0]
        for key, value in first_row.items():
            print(f"{key}: {value}")