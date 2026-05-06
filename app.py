import os
import re
import logging

from flask import Flask, request, jsonify, send_from_directory, redirect
from diagnosis_logic import run_diagnosis
from automation.tag_engine import classify_text
from automation.content_map import get_recommended_products
from email_generator import generate_email_subject, generate_email_html, generate_email_text
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="diagnosis_web")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APPS_SCRIPT_WEBHOOK_URL = os.getenv("APPS_SCRIPT_WEBHOOK_URL")

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
MAX_NAME_LENGTH = 100
MAX_FIELD_LENGTH = 200


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


@app.route("/")
@app.route("/index.html")
def index():
    return send_from_directory("diagnosis_web", "index.html")


@app.route("/questions")
@app.route("/questions.html")
def questions():
    return send_from_directory("diagnosis_web", "questions.html")


@app.route("/result")
@app.route("/result.html")
def result():
    return send_from_directory("diagnosis_web", "result.html")


@app.route("/complete")
@app.route("/complete.html")
def complete():
    return send_from_directory("diagnosis_web", "complete.html")


@app.route("/diagnosis")
@app.route("/start")
def diagnosis_start():
    return redirect("/questions?page=1")


def build_diagnosis_text(result: dict) -> str:
    parts = [
        str(result.get("parent_type", "")).strip(),
        str(result.get("relief", "")).strip(),
        str(result.get("structure", "")).strip(),
        str(result.get("theory", "")).strip(),
    ]
    return " ".join([p for p in parts if p])


def send_result_to_apps_script(payload: dict) -> dict:
    if not APPS_SCRIPT_WEBHOOK_URL:
        raise RuntimeError("APPS_SCRIPT_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
    response = requests.post(
        APPS_SCRIPT_WEBHOOK_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=20
    )
    response.raise_for_status()
    return response.json()


def validate_diagnosis_result_structure(diagnosis_result) -> bool:
    if not isinstance(diagnosis_result, dict):
        return False
    required_keys = {"parent_type", "scores", "diagnosis"}
    return required_keys.issubset(diagnosis_result.keys())


@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "요청 데이터가 없습니다."}), 400

        answers = data.get("answers", {})

        if not isinstance(answers, dict):
            return jsonify({"success": False, "error": "answers는 객체여야 합니다."}), 400

        required_keys = [f"q{i}" for i in range(1, 31)]
        missing = [k for k in required_keys if k not in answers or answers[k] in [None, ""]]

        if missing:
            return jsonify({
                "success": False,
                "error": f"응답 누락: {', '.join(missing[:5])}"
            }), 400

        answers_list = [answers.get(f"q{i}") for i in range(1, 31)]

        result = run_diagnosis(answers_list)

        diagnosis_text = build_diagnosis_text(result)
        tag_result = classify_text(diagnosis_text)
        products = get_recommended_products(tag_result)

        result["display_tags"] = [
            tag_result.get("display_tag_1", ""),
            tag_result.get("display_tag_2", ""),
            tag_result.get("display_tag_3", ""),
        ]

        result["recommended_products"] = [
            products.get("product_1", ""),
            products.get("product_2", ""),
            products.get("product_3", ""),
        ]

        result["internal_tags"] = {
            "type_primary": tag_result.get("type_primary", ""),
            "module_primary": tag_result.get("module_primary", ""),
            "framework_stage": tag_result.get("framework_stage", ""),
        }

        return jsonify({
            "success": True,
            "result": result
        })

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    except Exception as e:
        logger.error("진단 처리 오류: %s", e)
        return jsonify({
            "success": False,
            "error": "진단 처리 중 오류가 발생했습니다. 다시 시도해주세요."
        }), 500


@app.route("/api/submit-lead", methods=["POST"])
def submit_lead():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "요청 데이터가 없습니다."}), 400

        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        diagnosis_result = data.get("diagnosis_result")

        if not name:
            return jsonify({"success": False, "error": "name 값이 필요합니다."}), 400

        if len(name) > MAX_NAME_LENGTH:
            return jsonify({"success": False, "error": f"이름은 {MAX_NAME_LENGTH}자 이내여야 합니다."}), 400

        if not email:
            return jsonify({"success": False, "error": "email 값이 필요합니다."}), 400

        if len(email) > MAX_FIELD_LENGTH:
            return jsonify({"success": False, "error": "이메일 형식이 올바르지 않습니다."}), 400

        if not EMAIL_PATTERN.match(email):
            return jsonify({"success": False, "error": "이메일 형식이 올바르지 않습니다."}), 400

        if not diagnosis_result:
            return jsonify({"success": False, "error": "diagnosis_result 값이 필요합니다."}), 400

        if not validate_diagnosis_result_structure(diagnosis_result):
            return jsonify({"success": False, "error": "diagnosis_result 형식이 올바르지 않습니다."}), 400

        child_count = str(data.get("child_count", "")).strip()[:50]
        child_age = str(data.get("child_age", "")).strip()[:50]
        job = str(data.get("job", "")).strip()[:100]
        answers = data.get("answers")
        diagnosis_version = str(data.get("diagnosis_version", "")).strip()[:50]
        submitted_at = str(data.get("submitted_at", "")).strip()[:50]
        source = str(data.get("source", "")).strip()[:100]
        product_code = str(data.get("product_code", "")).strip()[:100]
        product_name = str(data.get("product_name", "")).strip()[:100]
        payment_status = str(data.get("payment_status", "")).strip()[:50]
        payment_provider = str(data.get("payment_provider", "")).strip()[:50]
        payment_order_id = str(data.get("payment_order_id", "")).strip()[:100]
        consent_privacy = bool(data.get("consent_privacy", False))
        consent_marketing = bool(data.get("consent_marketing", False))

        email_subject = generate_email_subject(diagnosis_result)
        email_body_html = generate_email_html(diagnosis_result)
        email_body_text = generate_email_text(diagnosis_result)

        safe_result = {k: v for k, v in diagnosis_result.items() if k != "answers"}

        payload = {
            "name": name,
            "email": email,
            "child_count": child_count,
            "child_age": child_age,
            "job": job,
            "answers": answers,
            "diagnosis_result": safe_result,
            "diagnosis_version": diagnosis_version,
            "submitted_at": submitted_at,
            "source": source,
            "product_code": product_code,
            "product_name": product_name,
            "payment_status": payment_status,
            "payment_provider": payment_provider,
            "payment_order_id": payment_order_id,
            "consent_privacy": consent_privacy,
            "consent_marketing": consent_marketing,
            "email_subject": email_subject,
            "email_body_html": email_body_html,
            "email_body_text": email_body_text,
        }

        script_result = send_result_to_apps_script(payload)

        if not isinstance(script_result, dict):
            return jsonify({
                "success": False,
                "error": "서버 처리 중 오류가 발생했습니다."
            }), 500

        if not script_result.get("success"):
            logger.error("Apps Script 처리 실패: %s", script_result.get("error"))
            return jsonify({
                "success": False,
                "error": "결과 전송 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            }), 500

        return jsonify({"success": True})

    except requests.exceptions.HTTPError as e:
        logger.error("Apps Script HTTP 오류: %s", e)
        return jsonify({
            "success": False,
            "error": "결과 전송 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        }), 500

    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
        }), 500

    except requests.exceptions.SSLError as e:
        logger.error("Apps Script SSL 오류: %s", e)
        return jsonify({
            "success": False,
            "error": "보안 연결 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        }), 500

    except requests.exceptions.RequestException as e:
        logger.error("외부 연동 오류: %s", e)
        return jsonify({
            "success": False,
            "error": "외부 서비스 연동 중 오류가 발생했습니다."
        }), 500

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except Exception as e:
        logger.error("리드 제출 처리 오류: %s", e)
        return jsonify({
            "success": False,
            "error": "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        }), 500


if __name__ == "__main__":
    if not APPS_SCRIPT_WEBHOOK_URL:
        logger.warning("APPS_SCRIPT_WEBHOOK_URL 환경변수가 설정되지 않았습니다. /api/submit-lead 기능이 비활성화됩니다.")
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
