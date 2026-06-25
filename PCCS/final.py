import os
import sys
import subprocess
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
import html  # ✅ 컬러칩 HTML 만들 때 사용

import gradio as gr

from openai_client import ask_openai, API_KEY

# -----------------------------
# 경로 설정
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent        # LP/PCCS
APP_PATH = BASE_DIR / "app.py"                    # LP/PCCS/app.py
UPLOAD_DIR = BASE_DIR / "uploads"                 # 업로드 이미지 저장
UPLOAD_DIR.mkdir(exist_ok=True)

# (참고용으로만 두고, 실제 시스템 프롬프트는 chat() 안에서 동적으로 생성)
SYSTEM_PROMPT_BASE = (
    "당신은 퍼스널컬러 전문가로서 친절하고 유익하게 상담해주는 챗봇입니다."
)


def extract_recommend_block(log_text: str) -> str:
    """
    app.py 출력(log_text)에서
    '최종 추천 TOP 5:' 이후의 립 추천 테이블만 뽑아서

    ▶ 인덱스 / RGB(r,g,b) / 뒤 로그는 제거하고
    ▶ '브랜드  옵션  #HEX' 형식의 줄들만 반환.
    """
    lines = log_text.splitlines()
    start = None

    # 1) '최종 추천 TOP 5'가 나오는 줄 위치 찾기
    for i, line in enumerate(lines):
        if "최종 추천 TOP 5" in line:
            start = i
            break

    if start is None:
        return "추천 정보를 로그에서 찾지 못했습니다."

    result_lines = []

    # 2) 그 다음 줄부터 테이블 부분만 파싱
    for line in lines[start + 1:]:
        s = line.strip()
        if not s:
            # 빈 줄을 만나고 나서 이미 뭔가를 모았다면, 거기서 끝
            if result_lines:
                break
            else:
                continue

        # ▶ 테이블 이후의 로그가 시작되면 거기서 끝내기
        if s.startswith("[stderr]") \
           or s.startswith("립 합성 이미지 생성 중") \
           or "옵션 저장 완료" in s:
            break

        # ▶ 헤더 줄(brand option hex r g b)은 건너뛰기
        if "brand" in s and "option" in s and "hex" in s:
            continue

        # ▶ 실제 데이터 줄만 처리 (hex 코드 포함)
        if "#" not in s:
            continue

        tokens = s.split()
        # 예상 형식: index, brand, option..., #HEX, r, g, b
        # ex) ['464','오아드','008브로위','#521C13','82','28','19']
        if len(tokens) < 4:
            continue

        # 마지막 3개는 r,g,b 이고, 그 앞이 hex 라고 가정
        hex_idx = -4
        if not tokens[hex_idx].startswith("#"):
            # 혹시 포맷이 달라졌으면 skip
            continue

        index = tokens[0]
        brand = tokens[1]
        hex_code = tokens[hex_idx]
        option_tokens = tokens[2:hex_idx]  # brand와 hex 사이가 옵션
        option = " ".join(option_tokens) if option_tokens else ""

        # "브랜드  옵션  #HEX" 형태로 정리
        if option:
            pretty_line = f"{brand}  {option}  {hex_code}"
        else:
            pretty_line = f"{brand}  {hex_code}"

        result_lines.append(pretty_line)

    if not result_lines:
        return "추천 정보를 로그에서 찾지 못했습니다."

    return "\n".join(result_lines)


def recommend_to_html(recommend_text: str) -> str:
    """
    '브랜드  옵션  #HEX' 형식의 추천 텍스트를 받아서
    각 줄 뒤에 작은 컬러칩(네모)을 붙인 HTML로 변환.
    """
    if not recommend_text:
        return "<div>추천 결과가 없습니다.</div>"

    lines = [line.strip() for line in recommend_text.splitlines() if line.strip()]
    html_lines = []

    for line in lines:
        tokens = line.split()
        hex_code = None

        # 맨 끝에서부터 #XXXXXX 형태 찾기
        for tok in reversed(tokens):
            if tok.startswith("#") and len(tok) in (4, 7):
                hex_code = tok
                break

        # 텍스트는 HTML 이스케이프
        safe_line = html.escape(line)

        if hex_code:
            chip = (
                f'<span style="display:inline-block;'
                f'width:14px;height:14px;'
                f'border-radius:3px;'
                f'background:{hex_code};'
                f'margin-left:8px;'
                f'border:1px solid #bbbbbb;'
                f'vertical-align:middle;"></span>'
            )
            html_lines.append(
                f'<div style="margin-bottom:4px;font-size:16px;">'
                f'{safe_line}{chip}</div>'
            )
        else:
            html_lines.append(
                f'<div style="margin-bottom:4px;font-size:16px;">{safe_line}</div>'
            )

    return "<div>" + "\n".join(html_lines) + "</div>"


def extract_season_block(log_text: str) -> str:
    """
    전체 log_text에서
    '판정된 시즌:' 줄부터
    피부 Lab/팔레트/립 데이터 로딩/stderr 직전까지 잘라서 반환.
    """
    lines = log_text.splitlines()
    start = None

    # 시작 지점: '판정된 시즌:' 이 있는 줄
    for i, line in enumerate(lines):
        if "판정된 시즌" in line:
            start = i
            break

    if start is None:
        # 못 찾으면 그냥 전체 로그를 그대로 보여주기 (fallback)
        return log_text

    block = []
    for line in lines[start:]:
        stripped = line.strip()

        # 여기서부터는 시즌 요약 이후 다른 섹션이 나오면 끊기
        if stripped.startswith("피부 Lab 위치 시각화") \
           or stripped.startswith("팔레트 합성 중") \
           or stripped.startswith("립 데이터 로딩 중") \
           or stripped.startswith("[stderr]"):
            break

        block.append(line)

    result = "\n".join(block).strip()
    return result if result else log_text


def clean_season_block(season_block: str) -> str:
    """
    시즌 블럭에서
    - 판정된 시즌: ...
    - skin_lab: ...
    - season_input: ...
    이 세 줄을 제거해서 반환.
    (로그 Textbox용)
    """
    if not season_block:
        return ""

    cleaned = []
    for line in season_block.splitlines():
        s = line.strip()
        if (
            s.startswith("판정된 시즌") or
            s.startswith("skin_lab:") or
            s.startswith("season_input:")
        ):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def make_season_title(shared_state) -> str:
    """
    shared_state["log"] (원본 전체 로그)에서
    '판정된 시즌:' 한 줄을 찾아
    시즌별로 색/크기/굵기를 준 HTML로 반환.
    """
    # shared_state가 dict 아닐 수도 있으니 방어코드
    if not isinstance(shared_state, dict):
        return ""

    full_log = shared_state.get("log") or ""
    if not full_log:
        return ""

    season_line = ""
    for line in full_log.splitlines():
        s = line.strip()
        if s.startswith("판정된 시즌"):
            season_line = s
            break

    if not season_line:
        return ""

    # 기본 색 (혹시 매칭 안될 때 대비)
    color = "#0C0506"

    # 시즌별 색상
    if "spring" in season_line or "봄" in season_line:
        color = "#EE6983"   # 봄웜
    elif "summer" in season_line or "여름" in season_line:
        color = "#3B82F6"   # 여름쿨
    elif "autumn" in season_line or "가을" in season_line:
        color = "#B45714"   # 가을웜
    elif "winter" in season_line or "겨울" in season_line:
        color = "#831B5B"   # 겨울쿨

    return (
        "<div style='font-size: 26px; "
        "font-weight: 800; "
        "text-align: center; "
        f"color: {color}; "
        "margin-bottom: 8px;'>"
        f"{season_line}"
        "</div>"
    )


# -----------------------------
# 1) 이미지 분석: app.py 서브프로세스로 실행
#   ➜ shared_state 에 최근 분석 결과 저장
# -----------------------------
def run_app(image, shared_state):
    """
    image: 업로드된 PIL 이미지
    shared_state: {"log": str, "recommend": str} 형태의 dict (gr.State로 전달됨)
    """
    # shared_state가 처음에는 None 일 수 있으므로 안전하게 초기화
    if shared_state is None or not isinstance(shared_state, dict):
        shared_state = {"log": "", "recommend": ""}

    # 이미지가 없을 때
    if image is None:
        # 기존 recommend 텍스트를 HTML로 변환해서 그대로 보여주기
        recommend_text = shared_state.get("recommend", "")
        recommend_html = recommend_to_html(recommend_text)
        return (
            "⚠️ 먼저 이미지를 업로드 해주세요.",
            recommend_html,
            None, None, None, None, None,
            shared_state,   # ✅ state도 함께 리턴
        )

    try:
        # 1) 업로드 이미지를 저장
        img_path = UPLOAD_DIR / "input.jpg"
        image.save(str(img_path))

        # 2) app.py 실행 (이미지 경로를 stdin으로 전달)
        cmd = [sys.executable, str(APP_PATH)]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(BASE_DIR),
        )
        out, err = proc.communicate(str(img_path) + "\n", timeout=600)

        # 3) stdout / stderr 분리해서 처리
        stdout_text = out or ""           # 👉 UI용 로그는 stdout만 사용
        full_log = stdout_text            # 👉 내부용 전체 로그 (stdout + stderr)

        if err:
            # 내부용 전체 로그에만 stderr를 붙여둔다
            full_log += "\n[stderr]\n" + err

        # 🔹 시즌 요약 블럭만 따로 추출 (탭1에서 보여줄용)
        raw_season_block = extract_season_block(full_log)
        season_block = clean_season_block(raw_season_block)

        # ✅ 로그에서 추천 제품 텍스트만 추출
        recommend_text = extract_recommend_block(full_log)
        # ✅ UI에서 바로 쓸 HTML로 변환
        recommend_html = recommend_to_html(recommend_text)

        # 4) app.py가 만든 결과 이미지 경로들
        img_dir = img_path.parent              # LP/PCCS/uploads
        test_dir = img_dir / "test_images"     # LP/PCCS/uploads/test_images

        face_box_img = img_dir / "face_box.jpg"
        facemesh_img = img_dir / "face_mesh_result.jpg"
        skin_pos_img = img_dir / "skin_position.jpg"
        palette_img = test_dir / "palette_result.jpg"
        lip_img = test_dir / "lip_result_1.jpg"

        # ✅ 5) 이번 분석 결과를 shared_state 에 저장 (챗봇용)
        shared_state["log"] = full_log          # 챗봇/디버깅용: stderr 포함
        shared_state["recommend"] = recommend_text  # 순수 텍스트 저장

        return (
            season_block,                              # 1: 탭1 시즌 로그 요약
            recommend_html,                            # 2: 탭2 HTML (텍스트 + 컬러칩)
            str(face_box_img) if face_box_img.exists() else None,
            str(facemesh_img) if facemesh_img.exists() else None,
            str(skin_pos_img) if skin_pos_img.exists() else None,
            str(palette_img) if palette_img.exists() else None,
            str(lip_img) if lip_img.exists() else None,
            shared_state,                              # 8: 공유 상태
        )

    except Exception as e:
        # 에러일 때도 8개 리턴 맞추기
        err_msg = f"❌ 실행 중 오류 발생: {e}"
        shared_state["log"] = err_msg
        shared_state["recommend"] = "추천 정보를 가져올 수 없습니다."
        recommend_html = recommend_to_html(shared_state["recommend"])
        return (
            err_msg,
            recommend_html,
            None, None, None, None, None,
            shared_state,
        )


def gradio_runner(image, shared_state):
    """
    Gradio에서 직접 호출할 래퍼 함수.
    - 내부에서 run_app을 호출하면서
    - stdout / stderr 로그를 전부 숨긴다.
    """
    # devnull(검은 구멍)에 출력 버리기
    with open(os.devnull, "w") as devnull:
        with redirect_stdout(devnull), redirect_stderr(devnull):
            result = run_app(image, shared_state)

    # run_app이 이미 8개 값을 튜플로 리턴하니까 그대로 돌려주면 됨
    return result


# -----------------------------
# 2) 퍼스널컬러 상담 챗봇
#    ➜ shared_state 를 참고해서 1탭 정보 활용
# -----------------------------
def is_pc_related(text: str) -> bool:
    """퍼스널컬러 관련 질문만 필터링"""
    keywords = [
        "퍼스널컬러", "퍼스널 컬러", "톤", "웜톤", "쿨톤",
        "봄웜", "여름쿨", "가을웜", "겨울쿨",
        "봄", "여름", "가을", "겨울",
        "spring", "summer", "autumn", "winter",
        "색상", "립", "메이크업", "추천"
    ]
    return any(k in text for k in keywords)


def chat(message, history, shared_state):
    """
    Gradio Chatbot 콜백.
    history 형식: [{"role": "user"/"assistant", "content": "..."} ...]
    shared_state: {"log": str, "recommend": str}
    """
    if history is None:
        history = []

    # 1) 퍼스널컬러 관련이 아니면 안내만
    if not is_pc_related(message):
        reply = "퍼스널컬러/톤/색상/립 등과 관련된 질문만 답변하고 있어요 😊"
        history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply},
        ]
        return history

    # ✅ shared_state 에서 최근 분석/추천 정보 꺼내기
    if not isinstance(shared_state, dict):
        shared_state = {"log": "", "recommend": ""}

    log_text = (shared_state.get("log") or "").strip()
    recommend_text = (shared_state.get("recommend") or "").strip()

    context_parts = []
    if log_text:
        context_parts.append("【최근 이미지 분석 로그 요약】\n" + log_text)
    if recommend_text:
        context_parts.append("【이미지 기반 립 제품 추천 TOP 5】\n" + recommend_text)

    if context_parts:
        pc_context = "\n\n".join(context_parts)
    else:
        pc_context = (
            "아직 이미지 분석 결과가 공유되지 않았습니다. "
            "일반적인 퍼스널컬러 이론과 사용자 질문만을 바탕으로 답변하세요."
        )

    # ✅ 이번 대화에 사용할 시스템 프롬프트 (1탭 정보 포함)
    system_prompt = {
        "role": "system",
        "content": (
            SYSTEM_PROMPT_BASE
            + "\n\n아래는 사용자의 최근 퍼스널컬러 분석/추천 정보입니다. "
              "가장 어울리는 퍼스널컬러는 득표수가 높은 시즌으로 판단하되, 득표수가 동률일 경우에는 색상거리가 짧은 시즌을 우선시하고 순위를 매겨 답변할때 참고하세요. "
              "대화 중 이 정보를 기억하고 적극 활용해 주세요.\n\n"
            + pc_context
        ),
    }

    # 2) 최근 대화 6쌍(=12개 메시지)만 context로 사용
    trimmed = history[-12:]

    messages = [system_prompt] + trimmed
    messages.append({"role": "user", "content": message})

    try:
        reply = ask_openai(messages)   # openai_client.ask_openai 사용
    except Exception as e:
        reply = f"API 호출 중 오류가 발생했어요: {e}"

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply},
    ]
    return history


# -----------------------------
# 3) Gradio UI
# -----------------------------
with gr.Blocks(title="PCCS 퍼스널컬러 분석 & 상담") as demo:
    # ✅ 탭 전체에서 공유할 state 정의
    #   log: 1탭 전체 로그
    #   recommend: 챗봇용 추천 텍스트
    shared_state = gr.State({"log": "", "recommend": ""})

    gr.HTML("""
    <style>
    /* 전체 기본 폰트 */
    body, .gradio-container * {
        font-family: "Noto Sans KR", system-ui, sans-serif;
    }

    /* 🔹 탭 줄 전체를 가운데 정렬 (role="tablist" 기준) */
    .gradio-container div[role="tablist"] {
        display: flex !important;           /* 혹시 flex가 아니더라도 강제로 flex */
        justify-content: center !important; /* 가운데 정렬 */
    }

    /* 탭 버튼 간격 조금만 띄우기 (선택사항) */
    .gradio-container div[role="tablist"] > button[role="tab"] {
        margin: 0 6px !important;
    }

    /* 🔹 상단 제목 스타일 */
    #main-title h2 {
        font-size: 30px;
        font-weight: 700;
        text-align: center;
        margin-top: 4px;
        margin-bottom: 12px;
        color: #000000 !important;
    }

    /* 🔹 탭 버튼 공통 스타일 (Gradio 4 기준: role="tab" 버튼) */
    .gradio-container button[role="tab"] {
        font-size: 18px !important;
        font-weight: 600 !important;
        text-align: center !important;
    }

    /*  이미지 분석 탭 */
    .gradio-container .tabs button[role="tab"]:nth-of-type(1) {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #EE6983 !important;
        text-align: center !important;
    }

    /*  제품 추천 탭 */
    .gradio-container .tabs button[role="tab"]:nth-of-type(2) {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #EE6983 !important;
        text-align: center !important;
    }

    /*  상담 챗봇 탭 */
    .gradio-container .tabs button[role="tab"]:nth-of-type(3) {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #EE6983 !important;
        text-align: center !important;
    }

    /* 🔹 로그 창 폰트 */
    #log-box textarea {
        font-size: 22px !important;
        line-height: 1.4;
    }

    /* 🔹 제품 추천 탭 추천 리스트 폰트 */
    #recommend-box {
        font-size: 35px !important;
        line-height: 1.5;
    }

    /* 🔹 분석 시작 버튼 색상 */
    #run-btn {
        background-color: #EE6983 !important;  /* 기본 배경색 */
        border-color: #ff7f50 !important;      /* 테두리색 */
        color: white !important;               /* 글자색 */
    }

    /* 마우스 올렸을 때 */
    #run-btn:hover {
        background-color: #850E35 !important;
        border-color: #850E35 !important;
    }
    /* 눌렀을 때 */
    #run-btn:active {
        background-color: #e9652e !important;
        border-color: #e9652e !important;
    }
    </style>
    """)

    title_md = gr.Markdown(
        "## 🌸🐰🌸톤순이🌸🐰🌸",
        elem_id="main-title"
    )

    # ===== 탭 1: 이미지 분석 =====
    with gr.Tab(" 이미지 분석"):
        with gr.Row():
            with gr.Column():
                input_img = gr.Image(
                    type="pil",
                    label="얼굴 사진 업로드"
                )
                run_btn = gr.Button("분석 시작", variant="primary", elem_id="run-btn")

                # ⭐ 판정된 시즌 한 줄만 크게/색 넣어서 보여줄 자리
                season_title = gr.Markdown(
                    "",
                    elem_id="season-title"
                )

                log_box = gr.Textbox(
                    label="로그 출력",
                    lines=15,
                    elem_id="log-box"
                )

            with gr.Column():
                face_box_out = gr.Image(label="얼굴 박스", type="filepath")
                facemesh_out = gr.Image(label="FaceMesh", type="filepath")
                skinpos_out = gr.Image(label="피부 위치(skin_position)", type="filepath")
                palette_out = gr.Image(label="시즌 팔레트 합성", type="filepath")
                lip_result_out = gr.Image(label="립 합성 (TOP1)", type="filepath")

    # ===== 탭 2: 제품 추천 =====
    with gr.Tab(" 제품 추천"):
        gr.Markdown("### 최종 추천 TOP 5 (텍스트)")
        # ✅ 텍스트 + 컬러칩을 한 번에 보여주는 HTML 컴포넌트
        recommend_box = gr.HTML(
            value="",
            elem_id="recommend-box"
        )

    # ===== 탭 3: 퍼스널컬러 상담 챗봇 =====
    with gr.Tab(" 퍼스널컬러 상담 챗봇"):
        gr.Markdown("퍼스널컬러/톤/립 관련 궁금한 걸 물어보세요!")
        chatbot = gr.Chatbot(label="대화창", height=500)
        msg = gr.Textbox(label="질문", placeholder="예: 여름쿨톤인데 립 추천해줘")
        clear_btn = gr.Button("🔁 대화 초기화")

        # ✅ shared_state 를 세 번째 인자로 넘겨서 1탭 정보 사용
        msg.submit(chat, [msg, chatbot, shared_state], chatbot)
        msg.submit(lambda: "", None, msg)
        clear_btn.click(lambda: [], None, chatbot)

    # ===== 버튼 동작 연결 =====
    analyze_event = run_btn.click(
        fn=run_app,
        inputs=[input_img, shared_state],
        outputs=[
            log_box,         # 1: 시즌 블럭 (skin_lab/season_input 제거됨)
            recommend_box,   # 2: 제품 추천 HTML (텍스트 + 컬러칩)
            face_box_out,    # 3
            facemesh_out,    # 4
            skinpos_out,     # 5
            palette_out,     # 6
            lip_result_out,  # 7
            shared_state,    # 8: 공유 상태
        ],
    )

    # 2) 시즌 블럭 내용을 이용해 '판정된 시즌: ...' 한 줄만 예쁘게 출력
    analyze_event.then(
        fn=make_season_title,
        inputs=shared_state,
        outputs=season_title,
    )


if __name__ == "__main__":
    demo.launch(
        debug=True,
        share=True
    )
