"""
email_generator.py
진단 결과 dict → email_subject / email_body_html / email_body_text 생성
"""

from __future__ import annotations
from typing import Any, Dict, List


# ──────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────

BRAND_NAME = "부모성장연구소"
BRAND_TAGLINE = "당신의 행복이 행복한 세상의 시작입니다"
COLOR_BG = "#FAF8F5"
COLOR_CARD = "#FFFFFF"
COLOR_HEADER_BG = "#0B132B"
COLOR_ACCENT = "#E2B05E"
COLOR_TEXT = "#2D2D2D"
COLOR_MUTED = "#666666"
COLOR_BORDER = "#E8E4DE"
COLOR_SCORE_BAR_FILL = "#E2B05E"
COLOR_SCORE_BAR_BG = "#EDE8E1"

THEORY_LABELS: Dict[str, str] = {
    "No Energy": "에너지 부족",
    "No Compass": "방향 부재",
    "No Action": "실행 실패",
    "No Energy + No Action": "에너지·실행 복합",
    "No Compass + No Energy": "방향·에너지 복합",
    "No Action + No Compass": "실행·방향 복합",
    "No Energy + No Compass + No Action": "전반적 과부하",
}


# ──────────────────────────────────────────────
# subject
# ──────────────────────────────────────────────

def generate_email_subject(result: Dict[str, Any]) -> str:
    parent_type = result.get("parent_type", "")
    return f"[부모성장연구소] {parent_type} 진단 결과 + 맞춤 실행 플랜이 도착했습니다"


# ──────────────────────────────────────────────
# 공통 HTML 컴포넌트
# ──────────────────────────────────────────────

def _score_bar_html(label: str, score: int, max_score: int = 30) -> str:
    pct = min(int(score / max_score * 100), 100)
    return f"""
    <tr>
      <td style="padding:4px 0;font-size:13px;color:{COLOR_TEXT};width:90px;">{label}</td>
      <td style="padding:4px 8px;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%">
          <tr>
            <td style="background:{COLOR_SCORE_BAR_BG};border-radius:4px;height:10px;overflow:hidden;">
              <div style="width:{pct}%;background:{COLOR_SCORE_BAR_FILL};height:10px;border-radius:4px;"></div>
            </td>
          </tr>
        </table>
      </td>
      <td style="padding:4px 0;font-size:13px;color:{COLOR_TEXT};width:40px;text-align:right;">{score}점</td>
    </tr>"""


def _section_header(title: str) -> str:
    return f"""
    <tr>
      <td style="padding:28px 0 12px;font-size:17px;font-weight:700;color:{COLOR_HEADER_BG};
                 border-bottom:2px solid {COLOR_ACCENT};">{title}</td>
    </tr>"""


def _text_row(text: str, padding_top: str = "12px") -> str:
    return f"""
    <tr>
      <td style="padding-top:{padding_top};font-size:14px;line-height:1.8;color:{COLOR_TEXT};">{text}</td>
    </tr>"""


def _label_value_row(label: str, value: str) -> str:
    return f"""
    <tr>
      <td style="padding-top:10px;">
        <span style="display:inline-block;background:{COLOR_ACCENT};color:#fff;
                     font-size:11px;font-weight:700;padding:2px 8px;border-radius:3px;
                     margin-bottom:4px;">{label}</span><br>
        <span style="font-size:14px;color:{COLOR_TEXT};line-height:1.7;">{value}</span>
      </td>
    </tr>"""


def _checklist_html(items: List[str]) -> str:
    rows = ""
    for item in items:
        rows += f"""
      <tr>
        <td style="padding:6px 0;font-size:14px;color:{COLOR_TEXT};line-height:1.6;">
          <span style="color:{COLOR_ACCENT};font-weight:700;margin-right:6px;">□</span>{item}
        </td>
      </tr>"""
    return f"<table width='100%' cellpadding='0' cellspacing='0' border='0'>{rows}</table>"


def _roadmap_html(roadmap: List[Dict[str, str]]) -> str:
    rows = ""
    for i, step_item in enumerate(roadmap, 1):
        step_label = step_item.get("step", f"{i}단계")
        step_action = step_item.get("action", "")
        rows += f"""
      <tr>
        <td style="padding:10px 0;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="background:{COLOR_HEADER_BG};color:#fff;font-size:12px;font-weight:700;
                         padding:4px 10px;border-radius:4px;width:1%;white-space:nowrap;">{step_label}</td>
              <td style="padding-left:12px;font-size:14px;color:{COLOR_TEXT};line-height:1.7;">{step_action}</td>
            </tr>
          </table>
        </td>
      </tr>"""
    return f"<table width='100%' cellpadding='0' cellspacing='0' border='0'>{rows}</table>"


# ──────────────────────────────────────────────
# HTML 이메일 본문 생성
# ──────────────────────────────────────────────

def generate_email_html(result: Dict[str, Any]) -> str:
    parent_type = result.get("parent_type", "")
    relief = result.get("relief", "")
    structure = result.get("structure", "")
    reason = result.get("reason", "")
    stop = result.get("stop", "")
    build = result.get("build", "")
    today = result.get("today", "")
    theory_raw = result.get("theory", "")
    theory_label = THEORY_LABELS.get(theory_raw, theory_raw)

    scores = result.get("scores", {})
    energy = scores.get("energy", 0)
    compass = scores.get("compass", 0)
    action = scores.get("action", 0)

    action_plan = result.get("action_plan", {})
    week1_focus = action_plan.get("week1_focus", "")
    first_step_label = action_plan.get("first_step_label", "")
    first_step_today = action_plan.get("first_step_today", "")
    first_step_why = action_plan.get("first_step_why", "")
    break_point_label = action_plan.get("break_point_label", "")
    break_point_insight = action_plan.get("break_point_insight", "")
    break_point_strategy = action_plan.get("break_point_strategy", "")
    collapse_cause = action_plan.get("collapse_cause", "")
    roadmap: List[Dict[str, str]] = action_plan.get("roadmap", [])
    checklist: List[str] = action_plan.get("checklist", [])

    score_bars = (
        _score_bar_html("No Energy", energy) +
        _score_bar_html("No Compass", compass) +
        _score_bar_html("No Action", action)
    )

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{BRAND_NAME} 진단 결과</title>
</head>
<body style="margin:0;padding:0;background:{COLOR_BG};font-family:'Apple SD Gothic Neo',Arial,sans-serif;">

<!-- 외부 래퍼 -->
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{COLOR_BG};">
<tr>
  <td align="center" style="padding:30px 16px;">

    <!-- 카드 컨테이너 -->
    <table width="600" cellpadding="0" cellspacing="0" border="0"
           style="max-width:600px;background:{COLOR_CARD};border-radius:12px;
                  box-shadow:0 2px 12px rgba(0,0,0,0.08);overflow:hidden;">

      <!-- ■ 헤더 -->
      <tr>
        <td style="background:{COLOR_HEADER_BG};padding:28px 32px;text-align:center;">
          <p style="margin:0;font-size:13px;color:{COLOR_ACCENT};letter-spacing:2px;font-weight:600;">
            {BRAND_NAME.upper()}
          </p>
          <p style="margin:6px 0 0;font-size:20px;color:#ffffff;font-weight:700;letter-spacing:-0.5px;">
            부모 성장 진단 결과
          </p>
          <p style="margin:8px 0 0;font-size:12px;color:rgba(255,255,255,0.6);">
            {BRAND_TAGLINE}
          </p>
        </td>
      </tr>

      <!-- ■ 본문 -->
      <tr>
        <td style="padding:32px;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0">

            <!-- 인사 -->
            <tr>
              <td style="font-size:15px;color:{COLOR_TEXT};line-height:1.8;padding-bottom:24px;
                         border-bottom:1px solid {COLOR_BORDER};">
                안녕하세요.<br>
                부모성장연구소에서 보내드리는 맞춤 진단 결과입니다.<br>
                진단에 참여해 주셔서 감사합니다.
              </td>
            </tr>

            <!-- ── SECTION 1: 무료 진단 요약 ── -->
            {_section_header("📊 나의 진단 유형")}

            <tr>
              <td style="padding-top:16px;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0"
                       style="background:#F5F2EC;border-radius:8px;padding:16px 20px;">
                  <tr>
                    <td>
                      <p style="margin:0;font-size:22px;font-weight:700;color:{COLOR_HEADER_BG};">
                        {parent_type}
                      </p>
                      <p style="margin:6px 0 0;font-size:13px;color:{COLOR_ACCENT};font-weight:600;">
                        {theory_label}
                      </p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            {_text_row(relief)}

            <!-- 점수 시각화 -->
            <tr>
              <td style="padding-top:20px;">
                <p style="margin:0 0 8px;font-size:13px;font-weight:600;color:{COLOR_MUTED};">3NO 점수 분포</p>
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                  {score_bars}
                </table>
              </td>
            </tr>

            {_section_header("🔍 구조 해석")}
            {_text_row(structure)}
            {_text_row(reason, "8px")}

            {_section_header("🎯 지금 당장 정리할 것")}
            {_label_value_row("멈춰야 할 것", stop)}
            {_label_value_row("세워야 할 것", build)}
            {_label_value_row("오늘 할 것", today)}

            <!-- ── SECTION 2: 상세 실행 플랜 ── -->
            <tr>
              <td style="padding:32px 0 16px;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0"
                       style="background:{COLOR_HEADER_BG};border-radius:8px;">
                  <tr>
                    <td style="padding:14px 20px;text-align:center;">
                      <p style="margin:0;font-size:14px;color:{COLOR_ACCENT};font-weight:700;
                                letter-spacing:1px;">PREMIUM</p>
                      <p style="margin:4px 0 0;font-size:18px;color:#ffffff;font-weight:700;">
                        맞춤 실행 플랜
                      </p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <!-- 이번 주 핵심 행동 -->
            {_section_header("📅 이번 주 핵심 행동")}
            {_text_row(week1_focus)}

            <!-- 오늘 첫 번째 행동 -->
            {_section_header(f"▶ 오늘 첫 번째 행동 — {first_step_label}")}
            {_text_row(first_step_today)}
            <tr>
              <td style="padding-top:10px;padding-left:12px;border-left:3px solid {COLOR_ACCENT};">
                <p style="margin:0;font-size:13px;color:{COLOR_MUTED};font-style:italic;
                          line-height:1.7;">{first_step_why}</p>
              </td>
            </tr>

            <!-- 3단계 실행 로드맵 -->
            {_section_header("🗺️ 3단계 실행 로드맵")}
            <tr>
              <td style="padding-top:8px;">{_roadmap_html(roadmap)}</td>
            </tr>

            <!-- 끊기는 지점 분석 -->
            {_section_header(f"⚡ 끊기는 지점 분석 — {break_point_label}")}
            {_text_row(break_point_insight)}
            <tr>
              <td style="padding-top:12px;background:#F5F2EC;border-radius:6px;padding:14px 16px;">
                <p style="margin:0 0 6px;font-size:12px;font-weight:700;color:{COLOR_ACCENT};">
                  맞춤 전략
                </p>
                <p style="margin:0;font-size:14px;color:{COLOR_TEXT};line-height:1.8;">
                  {break_point_strategy}
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding-top:8px;font-size:13px;color:{COLOR_MUTED};">
                주요 붕괴 원인 분석: <strong style="color:{COLOR_TEXT};">{collapse_cause}</strong>
              </td>
            </tr>

            <!-- 행동 체크리스트 -->
            {_section_header("✅ 이번 주 행동 체크리스트")}
            <tr>
              <td style="padding-top:8px;background:#F5F2EC;border-radius:6px;padding:14px 16px;">
                {_checklist_html(checklist)}
              </td>
            </tr>

            <!-- CTA -->
            <tr>
              <td style="padding-top:36px;text-align:center;border-top:1px solid {COLOR_BORDER};">
                <p style="margin:0 0 16px;font-size:14px;color:{COLOR_MUTED};">
                  더 구체적인 실천이 필요하다면
                </p>
                <a href="https://parelaunchers.com"
                   style="display:inline-block;background:{COLOR_ACCENT};color:#fff;
                          font-size:14px;font-weight:700;padding:14px 32px;border-radius:8px;
                          text-decoration:none;letter-spacing:0.5px;">
                  부모성장연구소 바로가기
                </a>
              </td>
            </tr>

          </table>
        </td>
      </tr>

      <!-- ■ 푸터 -->
      <tr>
        <td style="background:#F5F2EC;padding:20px 32px;text-align:center;
                   border-top:1px solid {COLOR_BORDER};">
          <p style="margin:0;font-size:12px;color:{COLOR_MUTED};line-height:1.8;">
            {BRAND_NAME} | 이 메일은 진단 참여 시 제공된 이메일로 발송되었습니다.<br>
            수신을 원하지 않으시면 이 메일에 회신해 주세요.
          </p>
        </td>
      </tr>

    </table>
  </td>
</tr>
</table>

</body>
</html>"""

    return html


# ──────────────────────────────────────────────
# 플레인 텍스트 이메일 본문 생성
# ──────────────────────────────────────────────

def generate_email_text(result: Dict[str, Any]) -> str:
    parent_type = result.get("parent_type", "")
    relief = result.get("relief", "")
    structure = result.get("structure", "")
    reason = result.get("reason", "")
    stop = result.get("stop", "")
    build = result.get("build", "")
    today_action = result.get("today", "")
    theory_raw = result.get("theory", "")
    theory_label = THEORY_LABELS.get(theory_raw, theory_raw)

    scores = result.get("scores", {})
    energy = scores.get("energy", 0)
    compass = scores.get("compass", 0)
    action = scores.get("action", 0)

    ap = result.get("action_plan", {})
    week1_focus = ap.get("week1_focus", "")
    first_step_label = ap.get("first_step_label", "")
    first_step_today = ap.get("first_step_today", "")
    first_step_why = ap.get("first_step_why", "")
    break_point_label = ap.get("break_point_label", "")
    break_point_insight = ap.get("break_point_insight", "")
    break_point_strategy = ap.get("break_point_strategy", "")
    collapse_cause = ap.get("collapse_cause", "")
    roadmap: List[Dict[str, str]] = ap.get("roadmap", [])
    checklist: List[str] = ap.get("checklist", [])

    roadmap_lines = "\n".join(
        f"  [{item.get('step', '')}] {item.get('action', '')}" for item in roadmap
    )
    checklist_lines = "\n".join(f"  □ {item}" for item in checklist)

    return f"""[부모성장연구소] 맞춤 진단 결과 + 실행 플랜

안녕하세요.
부모성장연구소에서 보내드리는 맞춤 진단 결과입니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 나의 진단 유형
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

유형: {parent_type} ({theory_label})

3NO 점수:
  No Energy  : {energy}점 / 30점
  No Compass : {compass}점 / 30점
  No Action  : {action}점 / 30점

{relief}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 구조 해석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{structure}

{reason}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 지금 당장 정리할 것
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[멈춰야 할 것] {stop}
[세워야 할 것] {build}
[오늘 할 것] {today_action}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 이번 주 핵심 행동
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{week1_focus}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ 오늘 첫 번째 행동 — {first_step_label}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{first_step_today}

왜 이것인가?
{first_step_why}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗺️ 3단계 실행 로드맵
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{roadmap_lines}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ 끊기는 지점 분석 — {break_point_label}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{break_point_insight}

맞춤 전략:
{break_point_strategy}

주요 붕괴 원인: {collapse_cause}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 이번 주 행동 체크리스트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{checklist_lines}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

부모성장연구소
"{BRAND_TAGLINE}"

수신을 원하지 않으시면 이 메일에 회신해 주세요.
"""
