def reverse_score(score):
    """역문항 점수 변환: 1->5, 2->4, 3->3, 4->2, 5->1"""
    return 6 - score


def validate_answers(answers):
    """
    30문항 구조 검증
    - 1~18: 1~5 정수
    - 19~28: 1~5 정수 (선택형)
    - 29~30: 문자열
    """
    if not isinstance(answers, list):
        raise ValueError("answers는 리스트여야 합니다.")

    if len(answers) != 30:
        raise ValueError("문항 수는 30개여야 합니다.")

    # 1~18: 리커트 점수형
    for i in range(18):
        score = answers[i]
        if not isinstance(score, int):
            raise ValueError(f"{i + 1}번 문항 응답은 정수여야 합니다.")
        if score < 1 or score > 5:
            raise ValueError(f"{i + 1}번 문항 응답은 1~5 사이여야 합니다.")

    # 19~28: 선택형
    for i in range(18, 28):
        score = answers[i]
        if not isinstance(score, int):
            raise ValueError(f"{i + 1}번 문항 응답은 정수여야 합니다.")
        if score < 1 or score > 5:
            raise ValueError(f"{i + 1}번 문항 응답은 1~5 사이여야 합니다.")

    # 29~30: 서술형
    for i in range(28, 30):
        value = answers[i]
        if not isinstance(value, str):
            raise ValueError(f"{i + 1}번 문항 응답은 문자열이어야 합니다.")
        if not value.strip():
            raise ValueError(f"{i + 1}번 문항 응답은 비어 있을 수 없습니다.")
        if len(value) > 1000:
            raise ValueError(f"{i + 1}번 문항 응답은 1000자 이내여야 합니다.")


def calculate_scores(answers):
    """
    answers: 1~30번 질문에 대한 리스트
    실제 점수 계산은 1~18번만 사용
    """

    validate_answers(answers)

    energy = sum(answers[0:6])

    compass = (
        sum(answers[6:11]) +
        reverse_score(answers[11])   # Q12R
    )

    action = (
        sum(answers[12:16]) +
        reverse_score(answers[16]) +  # Q17R
        reverse_score(answers[17])    # Q18R
    )

    return {
        "energy": energy,
        "compass": compass,
        "action": action
    }


def diagnose(scores):
    """
    1차 3No 진단
    """
    energy = scores["energy"]
    compass = scores["compass"]
    action = scores["action"]

    max_score = max(scores.values())

    if max_score == energy:
        return "No Energy"
    elif max_score == compass:
        return "No Compass"
    else:
        return "No Action"


def get_energy_subscores(answers):
    """
    Energy 세부 판별용
    방전형: Q1, Q3, Q6
    예민과부하형: Q2, Q4, Q5
    """
    drained = answers[0] + answers[2] + answers[5]       # Q1, Q3, Q6
    overload = answers[1] + answers[3] + answers[4]      # Q2, Q4, Q5
    return drained, overload


def get_compass_subscores(answers):
    """
    Compass 세부 판별용
    기준흔들림형: Q7, Q9, Q12R
    비교불안형: Q8, Q10, Q11
    """
    compass_core = answers[6] + answers[8] + reverse_score(answers[11])   # Q7, Q9, Q12R
    comparison_anxiety = answers[7] + answers[9] + answers[10]            # Q8, Q10, Q11
    return compass_core, comparison_anxiety


def get_action_subscores(answers):
    """
    Action 세부 판별용
    실행흔들림형: Q13, Q14, Q15, Q17R, Q18R
    반복이탈형: Q16 + Compass 중간 이상 여부 참고
    """
    execution_wobble = (
        answers[12] + answers[13] + answers[14] +
        reverse_score(answers[16]) +
        reverse_score(answers[17])
    )
    repeated_drop = answers[15]   # Q16
    return execution_wobble, repeated_drop


def classify_single_type(scores, answers):
    """
    단일 유형 분류
    """
    energy = scores["energy"]
    compass = scores["compass"]
    action = scores["action"]

    if energy >= compass and energy >= action:
        drained, overload = get_energy_subscores(answers)

        if overload > drained and action >= 18:
            return "예민과부하형 부모"
        return "방전형 부모"

    if compass >= energy and compass >= action:
        compass_core, comparison_anxiety = get_compass_subscores(answers)

        if comparison_anxiety > compass_core and energy >= 18:
            return "비교불안형 부모"
        return "기준흔들림형 부모"

    execution_wobble, repeated_drop = get_action_subscores(answers)

    if repeated_drop >= 4 and compass >= 18:
        return "반복이탈형 부모"

    if repeated_drop >= 5 and compass >= 16:
        return "반복이탈형 부모"

    return "실행흔들림형 부모"


def classify_combo_type(scores, answers):
    """
    복합 유형 분류
    상위 2개 축 차이가 2점 이내
    """
    sorted_scores = sorted(
        [("energy", scores["energy"]), ("compass", scores["compass"]), ("action", scores["action"])],
        key=lambda x: x[1],
        reverse=True
    )

    first_name, first_score = sorted_scores[0]
    second_name, second_score = sorted_scores[1]

    if first_score - second_score > 2:
        return None

    combo = {first_name, second_name}

    if combo == {"energy", "compass"}:
        return "비교불안형 부모"

    if combo == {"energy", "action"}:
        return "예민과부하형 부모"

    if combo == {"compass", "action"}:
        return "반복이탈형 부모"

    return None


def classify_type(scores, answers):
    """
    최종 유형 분류
    우선순위:
    1) 전반적 과부하형
    2) 복합 유형
    3) 단일 유형
    """
    energy = scores["energy"]
    compass = scores["compass"]
    action = scores["action"]

    score_list = [energy, compass, action]
    max_score = max(score_list)
    min_score = min(score_list)

    # 전반적 과부하형
    if max_score - min_score <= 2 and min_score >= 18:
        return "전반적 과부하형 부모"

    combo_type = classify_combo_type(scores, answers)
    if combo_type:
        return combo_type

    return classify_single_type(scores, answers)


def get_result_content(parent_type):
    """
    결과 페이지용 구조화된 문구
    """
    content_map = {
        "방전형 부모": {
            "relief": "의지가 약한 것이 아니라, 지금은 마음보다 에너지가 먼저 무너지는 구조에 가깝습니다.",
            "structure": "문제 상황이 생겼을 때 기준이나 실행 이전에 에너지가 먼저 바닥나는 경향이 있습니다. 이 상태가 길어질수록 감정 조절보다 버티기가 먼저 되고, 관계와 후회가 반복되기 쉽습니다.",
            "reason": "더 잘해야 한다는 생각으로 버티지만, 실제로는 회복 구조가 없어서 같은 패턴이 반복되기 쉽습니다.",
            "stop": "더 버티려는 시도",
            "build": "하루 안의 짧은 회복 시간",
            "today": "잠들기 전 '지금 내 에너지는 몇 점인가?'를 적어보기",
            "theory": "No Energy 중심"
        },
        "예민과부하형 부모": {
            "relief": "성격 문제가 아니라, 지금은 지침과 과부하가 겹치며 예민함이 커지는 구조에 가깝습니다.",
            "structure": "지침과 과부하가 함께 쌓인 상태에서 부모 역할을 버티고 있어 예민함과 실행 어려움이 함께 나타나는 패턴입니다.",
            "reason": "이미 과부하 상태인데도 의지로만 눌러 보려 하기 때문에 작은 자극에도 반응이 커지고, 이후 후회와 피로가 반복되기 쉽습니다.",
            "stop": "예민함을 의지로 눌러버리려는 시도",
            "build": "자극을 줄이는 저녁 회복 구조",
            "today": "아이와 대화 전 5초 멈추고 내 몸 상태 먼저 확인하기",
            "theory": "No Energy + No Action"
        },
        "기준흔들림형 부모": {
            "relief": "의지가 부족한 것이 아니라, 지금은 에너지보다 기준이 먼저 흔들리는 구조에 가깝습니다.",
            "structure": "상황마다 판단 기준이 흔들리기 쉬워서 감정과 반응도 함께 흔들리는 패턴입니다. 정보가 늘수록 오히려 방향이 더 흐려질 수 있습니다.",
            "reason": "더 많은 정보를 모아도 우리 집 기준이 선명하지 않으면, 상황이 바뀔 때마다 다시 흔들리기 쉽습니다.",
            "stop": "상황마다 기준을 바꾸는 반응적 판단",
            "build": "우리 집에서 중요한 기준 1개",
            "today": "'우리 집에서 가장 지키고 싶은 한 가지'를 한 문장으로 적기",
            "theory": "No Compass 중심"
        },
        "비교불안형 부모": {
            "relief": "부족한 부모라서가 아니라, 지금은 기준이 외부로 이동해 있어 스스로를 자주 의심하는 구조에 가깝습니다.",
            "structure": "비교와 불안이 커질수록 내 기준보다 외부 시선이 더 커지고, 그 결과 판단과 감정이 함께 흔들리는 패턴입니다.",
            "reason": "내 기준이 선명하지 않을 때 비교는 더 커집니다. 그래서 문제는 의지가 아니라 기준의 위치일 수 있습니다.",
            "stop": "다른 부모의 방식과 내 상태를 바로 비교하는 습관",
            "build": "외부 평가보다 먼저 보는 내 기준",
            "today": "오늘 내가 잘한 부모 행동 1가지를 적어보기",
            "theory": "No Compass + No Energy"
        },
        "실행흔들림형 부모": {
            "relief": "의지가 없는 것이 아니라, 지금은 알고 있어도 유지되지 않는 실행 흔들림 구조에 가깝습니다.",
            "structure": "무엇을 해야 하는지는 알지만 지속되지 않고, 루틴이 쉽게 무너지는 패턴이 강합니다.",
            "reason": "큰 결심과 계획은 있지만 끊기지 않는 최소 구조가 없으면, 반복해서 시작하고 무너지는 흐름이 이어지기 쉽습니다.",
            "stop": "큰 계획부터 세우는 방식",
            "build": "작아도 매일 가능한 최소 루틴",
            "today": "내일 반복할 행동 1개만 정해서 적기",
            "theory": "No Action 중심"
        },
        "반복이탈형 부모": {
            "relief": "게으른 것이 아니라, 지금은 시작은 하지만 정착되지 못하고 흐름에서 자주 이탈하는 구조에 가깝습니다.",
            "structure": "새로 시작하는 힘은 있지만, 어디서 끊기는지 보지 못해 반복적으로 흐름에서 이탈하는 패턴이 강합니다.",
            "reason": "새 방법을 찾는 데 에너지를 쓰지만, 실제로는 끊기는 지점을 기록하고 이해하는 구조가 없어서 같은 이탈이 반복되기 쉽습니다.",
            "stop": "매번 새 방법만 찾는 시도",
            "build": "끊기는 지점을 기록하는 구조",
            "today": "최근 3일 중 무너진 순간 1가지를 적고, 어디서 끊겼는지 표시하기",
            "theory": "No Action + No Compass"
        },
        "전반적 과부하형 부모": {
            "relief": "의지가 약한 것이 아니라, 지금은 에너지·기준·실행이 함께 흔들리고 있는 구조에 가깝습니다.",
            "structure": "한 축만의 문제가 아니라 에너지, 기준, 실행이 전반적으로 함께 흔들리고 있는 상태입니다. 이럴 때는 한 가지 해결책을 더하는 것보다 전체 흐름을 먼저 느리게 만드는 것이 필요합니다.",
            "reason": "모든 걸 한 번에 바로잡으려 하면 회복보다 압박이 더 커지고, 그 결과 다시 전반적 과부하로 돌아가기 쉽습니다.",
            "stop": "모든 걸 한 번에 바로잡으려는 시도",
            "build": "가장 먼저 회복할 한 축의 우선순위",
            "today": "Energy / Compass / Action 중 지금 가장 먼저 무너진 하나를 고르기",
            "theory": "No Energy + No Compass + No Action"
        }
    }

    if parent_type not in content_map:
        raise ValueError(f"알 수 없는 유형입니다: {parent_type}")

    return content_map[parent_type]


def recommend_product(parent_type):
    recommendations = {
        "방전형 부모": {
            "magazine": "회복형 매거진 1편",
            "guide": "하루 10분 부모 리셋 가이드",
            "product": "에너지 회복 루틴 프로그램"
        },
        "예민과부하형 부모": {
            "magazine": "과부하 해석 매거진",
            "guide": "저녁 회복 루틴 가이드",
            "product": "감정 과부하 해소 프로그램"
        },
        "기준흔들림형 부모": {
            "magazine": "기준 설계 매거진 1편",
            "guide": "우리 집 기준 정리 워크시트",
            "product": "부모 기준 설계 워크북 / 방향 회복 프로그램"
        },
        "비교불안형 부모": {
            "magazine": "비교 멈춤 매거진",
            "guide": "자기 기준 회복 워크시트",
            "product": "불안 정리 프로그램 / 기준 회복 코스"
        },
        "실행흔들림형 부모": {
            "magazine": "실행 루틴 매거진",
            "guide": "5분 루틴 설계 가이드",
            "product": "지속 가능한 부모 루틴 프로그램"
        },
        "반복이탈형 부모": {
            "magazine": "반복 패턴 해석 매거진",
            "guide": "반복 이탈 분석 워크시트",
            "product": "루틴 재연결 프로그램 / 맞춤 구조 코칭"
        },
        "전반적 과부하형 부모": {
            "magazine": "전반적 과부하 해석 매거진",
            "guide": "우선순위 재정렬 가이드",
            "product": "초기 회복 리셋 프로그램 / 1:1 구조 진단 코칭"
        }
    }

    if parent_type not in recommendations:
        raise ValueError(f"알 수 없는 유형입니다: {parent_type}")

    return recommendations[parent_type]


def get_extended_context(answers):
    """
    19~30번 응답을 결과 보조 정보로 구조화
    """
    return {
        "time_slot": answers[18],              # Q19
        "first_reaction": answers[19],         # Q20
        "afterthought": answers[20],           # Q21
        "break_point": answers[21],            # Q22
        "main_burden": answers[22],            # Q23
        "change_goal": answers[23],            # Q24
        "first_action": answers[24],           # Q25
        "after_conflict_pattern": answers[25], # Q26
        "collapse_cause": answers[26],         # Q27
        "self_state": answers[27],             # Q28
        "collapse_scene": answers[28].strip(), # Q29
        "priority_change": answers[29].strip() # Q30
    }


def run_diagnosis(answers):
    """
    Flask app.py에서 호출할 통합 진단 함수
    answers: 길이 30의 리스트
    """
    from action_plan import generate_action_plan

    scores = calculate_scores(answers)
    diagnosis_result = diagnose(scores)
    parent_type = classify_type(scores, answers)
    recommendation = recommend_product(parent_type)
    result_content = get_result_content(parent_type)
    extended_context = get_extended_context(answers)
    action_plan = generate_action_plan(answers, parent_type)

    return {
        "scores": scores,
        "diagnosis": diagnosis_result,
        "parent_type": parent_type,
        "relief": result_content["relief"],
        "structure": result_content["structure"],
        "reason": result_content["reason"],
        "stop": result_content["stop"],
        "build": result_content["build"],
        "today": result_content["today"],
        "theory": result_content["theory"],
        "recommendation": recommendation,
        "extended_context": extended_context,
        "action_plan": action_plan,
    }


if __name__ == "__main__":
    sample = [
        3, 4, 4, 3, 3, 4,
        3, 4, 3, 4, 3, 2,
        4, 3, 4, 3, 2, 2,
        3, 1, 4, 2, 2, 4, 1, 3, 5, 2,
        "아이가 말을 안 들을 때 갑자기 화를 크게 냈다",
        "저녁에 감정적으로 반응하지 않도록 조절하고 싶다"
    ]

    result = run_diagnosis(sample)

    print("점수:", result["scores"])
    print("1차 진단:", result["diagnosis"])
    print("유형:", result["parent_type"])
    print("한 줄 안도:", result["relief"])
    print("멈춰야 할 것:", result["stop"])
    print("세워야 할 것:", result["build"])
    print("오늘 할 것:", result["today"])
    print("추천 매거진:", result["recommendation"]["magazine"])
    print("추천 가이드:", result["recommendation"]["guide"])
    print("추천 상품:", result["recommendation"]["product"])
    print("확장 맥락:", result["extended_context"])