from flask import Flask, request, jsonify, send_from_directory, redirect
from diagnosis_logic import run_diagnosis
from automation.tag_engine import classify_text
from automation.content_map import get_recommended_products
import requests

app = Flask(__name__, static_folder="diagnosis_web")

APPS_SCRIPT_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwQJgGtewBw7TncZO7bskFLmSQ67HyUrjbn5QY4bs38rRg2Pfo9QcTF1ETWP_PjTlDE/exec"


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
    """
    run_diagnosis 결과를 하나의 텍스트로 합쳐
    tag_engine 분류에 사용할 입력값을 만든다.
    """
    parts = [
        str(result.get("parent_type", "")).strip(),
        str(result.get("relief", "")).strip(),
        str(result.get("structure", "")).strip(),
        str(result.get("theory", "")).strip(),
    ]
    return " ".join([p for p in parts if p])


@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "요청 데이터가 없습니다."}), 400

        answers = data.get("answers")

        if not isinstance(answers, list):
            return jsonify({"success": False, "error": "answers는 리스트여야 합니다."}), 400

        result = run_diagnosis(answers)

        # -----------------------------
        # TAG + 추천 상품 자동 생성
        # -----------------------------
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

        # 관리자/내부용 태그도 함께 저장
        result["internal_tags"] = {
            "type_primary": tag_result.get("type_primary", ""),
            "module_primary": tag_result.get("module_primary", ""),
            "framework_stage": tag_result.get("framework_stage", ""),
        }

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
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

        if not email:
            return jsonify({"success": False, "error": "email 값이 필요합니다."}), 400

        if not diagnosis_result:
            return jsonify({"success": False, "error": "diagnosis_result 값이 필요합니다."}), 400

        payload = {
            "name": name,
            "email": email,
            "child_count": str(data.get("child_count", "")).strip(),
            "child_age": str(data.get("child_age", "")).strip(),
            "job": str(data.get("job", "")).strip(),
            "diagnosis_result": diagnosis_result
        }

        response = requests.post(
            APPS_SCRIPT_WEBHOOK_URL,
            json=payload,
            timeout=20
        )

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "error": f"Apps Script 전송 실패: HTTP {response.status_code}"
            }), 500

        try:
            script_result = response.json()
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Apps Script 응답이 JSON 형식이 아닙니다."
            }), 500

        if not script_result.get("success"):
            return jsonify({
                "success": False,
                "error": script_result.get("error", "Apps Script 처리 실패")
            }), 500

        return jsonify({"success": True})

    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "error": f"외부 연동 오류: {str(e)}"
        }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)