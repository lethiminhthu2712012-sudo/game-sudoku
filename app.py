import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import random
import html

st.set_page_config(page_title="Sudoku", page_icon="🌸", layout="wide")

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

SOLUTION = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]

LEVELS = [
    ("Màn 1 · Nụ hoa", 38),
    ("Màn 2 · Cánh hoa", 32),
    ("Màn 3 · Vườn xuân", 28),
    ("Màn 4 · Mưa hoa", 24),
    ("Màn 5 · Sakura", 20),
]


def make_puzzle(level):
    keep = LEVELS[level][1]
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.Random(2026 + level).shuffle(cells)

    puzzle = [row[:] for row in SOLUTION]

    for r, c in cells[:81 - keep]:
        puzzle[r][c] = 0

    return puzzle


def data_uri(path):
    if not path.is_file():
        return ""

    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(path.suffix.lower(), "image/png")

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")

    return f"data:{mime};base64,{encoded}"


def audio_uri(filename):
    path = ASSETS / filename

    if not path.is_file():
        return None

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")

    return f"data:audio/mpeg;base64,{encoded}"


def play_effect(kind):
    files = {
        "click": "sounds_click.mp3",
        "win": "sounds_win.mp3",
        "lose": "sounds_lose.mp3",
    }

    src = audio_uri(files.get(kind, "sounds_click.mp3"))

    if src:
        components.html(
            f'<audio autoplay><source src="{src}" type="audio/mpeg"></audio>',
            height=0,
        )


def inject_background(path):
    uri = data_uri(path)
    background = ""

    if uri:
        background = f"""
        background-image:
          linear-gradient(rgba(255,247,249,.35), rgba(255,247,249,.45)),
          url("{uri}");
        """

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Yeseva+One&display=swap');

    html, body, [class*="st-"], button, input, label, p, h1, h2, h3,
    span, div, textarea {{
        font-family: 'Yeseva One', Georgia, serif !important;
    }}

    .stApp {{
        {background}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #70243f;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    .block-container {{
        padding-top: 1.5rem;
        max-width: 1250px;
    }}

    h1, h2, h3, p, label,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {{
        color: #70243f;
    }}

    h1 {{
        font-size: clamp(40px, 5vw, 60px) !important;
    }}

    h2 {{
        font-size: 38px !important;
    }}

    h3 {{
        font-size: 30px !important;
    }}

    p, label, .stCaption,
    [data-testid="stMarkdownContainer"] {{
        font-size: 21px;
        line-height: 1.6;
    }}

    .subtitle {{
        color: #70243f;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
    }}

    div.stButton > button {{
        color: #70243f !important;
        background: #f8dce6 !important;
        border: 2px solid #cf7896 !important;
        border-radius: 18px !important;
        min-height: 56px;
        font-size: 21px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 12px #8d385020;
    }}

    div.stButton > button:hover {{
        background: #edb4c8 !important;
        border-color: #a83f65 !important;
    }}

    div.stButton > button:disabled {{
        background: #eadde1 !important;
        color: #79636b !important;
        border-color: #c7afb8 !important;
    }}

    div[data-baseweb="select"] > div {{
        background: #fff8fa;
        border-color: #bd6686;
        color: #70243f;
        min-height: 48px;
    }}

    [data-testid="stAlert"] {{
        background: rgba(255,249,251,.97);
        border: 1px solid #d990a6;
    }}
    </style>
    """, unsafe_allow_html=True)


def go(page):
    st.session_state.page = page
    st.rerun()


for key, default in {
    "page": "menu",
    "level": 0,
    "unlocked": 0,
    "completed": [],
    "status": "playing",
    "board": None,
    "puzzle": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


PETALS = """
<style>
.petal {
    position: fixed;
    top: -60px;
    z-index: 999;
    pointer-events: none;
    user-select: none;
    opacity: .82;
    animation: petal-fall linear infinite;
}

@keyframes petal-fall {
    0% {
        transform: translateY(-5vh) rotate(0deg);
    }
    100% {
        transform: translateY(115vh) rotate(600deg);
    }
}
</style>

<div aria-hidden="true">
    <span class="petal"
          style="left:5%;font-size:22px;animation-duration:10s">🌸</span>

    <span class="petal"
          style="left:17%;font-size:17px;animation-duration:13s;animation-delay:2s">🌸</span>

    <span class="petal"
          style="left:31%;font-size:23px;animation-duration:11s;animation-delay:1s">🌸</span>

    <span class="petal"
          style="left:47%;font-size:18px;animation-duration:14s;animation-delay:4s">🌸</span>

    <span class="petal"
          style="left:63%;font-size:22px;animation-duration:12s;animation-delay:3s">🌸</span>

    <span class="petal"
          style="left:78%;font-size:19px;animation-duration:10s;animation-delay:1s">🌸</span>

    <span class="petal"
          style="left:92%;font-size:24px;animation-duration:15s;animation-delay:5s">🌸</span>
</div>
"""


# =========================
# MENU CHÍNH
# =========================

if st.session_state.page == "menu":

    uri = data_uri(ASSETS / "menu.png")
    bg = ""

    if uri:
        bg = (
            f'background-image:linear-gradient('
            f'rgba(255,247,249,.08),rgba(255,247,249,.08)),'
            f'url("{uri}");'
        )

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Yeseva+One&display=swap');

    html, body, [class*="st-"], button, p, h1, h2, span, div {{
        font-family: 'Yeseva One', Georgia, serif !important;
    }}

    .stApp {{
        {bg}
        background-size: cover !important;
        background-position: center center !important;
        background-attachment: fixed !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    .block-container {{
        padding-top: 1.5rem;
        max-width: 1200px;
    }}

    .menu-title {{
        text-align: center;
        font-size: clamp(90px, 13vw, 170px);
        line-height: 1.15;
        font-weight: 900;
        color: #e52f79;
        -webkit-text-stroke: 1px #fff0f5;
        text-shadow:
            0 3px 0 #fff2f6,
            0 8px 25px rgba(130,24,68,.35);
        margin: 0 auto;
    }}

    div.stButton > button {{
        color: #9c174c !important;
        background: linear-gradient(145deg, #fff0f6, #ef9fbe) !important;
        border: 4px solid #d84e86 !important;
        border-radius: 50% !important;
        width: 220px !important;
        height: 220px !important;
        min-height: 220px !important;
        white-space: pre-line !important;
        font-size: 32px !important;
        line-height: 1.3 !important;
        font-weight: bold !important;
        box-shadow:
            0 0 0 9px rgba(255,239,246,.72),
            0 10px 28px rgba(117,39,69,.28);
        transition: transform .2s ease;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(145deg, #ffe1ed, #e97da8) !important;
        transform: scale(1.06);
    }}

    .petal {{
        position: fixed;
        top: -60px;
        z-index: 999;
        pointer-events: none;
        user-select: none;
        opacity: .85;
        animation: petal-fall linear infinite;
    }}

    @keyframes petal-fall {{
        0% {{
            transform: translateY(-5vh) rotate(0deg);
        }}
        100% {{
            transform: translateY(115vh) rotate(600deg);
        }}
    }}
    </style>

    <h1 class="menu-title">Sudoku</h1>
    """, unsafe_allow_html=True)

    st.markdown(PETALS, unsafe_allow_html=True)

    # Người chơi nhấn Play để bật nhạc nền.
    # Trình duyệt thường chặn âm thanh tự phát.

    music_src = audio_uri("sounds_bgm.mp3")

    if music_src:
        st.markdown(f"""
        <div style="
            max-width:340px;
            margin:14px auto 0;
            text-align:center;
            color:#70243f;
            font-size:19px;
            font-weight:bold;
        ">
            🌸 Nhạc nền — nhấn Play để bật 🌸

            <audio controls loop preload="auto"
                   style="display:block;width:100%;margin-top:8px">
                <source src="{music_src}" type="audio/mpeg">
                Trình duyệt không hỗ trợ MP3.
            </audio>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error(
            "Không tìm thấy assets/sounds_bgm.mp3. "
            "Hãy kiểm tra tên file."
        )

    st.markdown(
        "<div style='height:8vh'></div>",
        unsafe_allow_html=True
    )

    _, center, _ = st.columns([1, 1, 1])

    with center:
        if st.button(
            "🌸\nPLAY NOW\n🌸",
            key="start_game",
            use_container_width=True
        ):
            go("levels")

    st.markdown(
        "<div style='height:5vh'></div>",
        unsafe_allow_html=True
    )


# =========================
# CHỌN MÀN CHƠI
# =========================

elif st.session_state.page == "levels":

    inject_background(ASSETS / "game_bg.png")

    st.markdown(
        "<h1 style='text-align:center;color:#e52f79;font-size:56px'>"
        "Chọn màn chơi</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p class='subtitle'>Chọn một khu vườn để bắt đầu 🌸</p>",
        unsafe_allow_html=True
    )

    cols = st.columns(5, gap="medium")

    for i, col in enumerate(cols):

        with col:

            unlocked = i <= st.session_state.unlocked
            done = i in st.session_state.completed

            icon = "🌸" if done else ("🔓" if unlocked else "🔒")

            st.markdown(f"""
            <div style="text-align:center;padding:12px 2px">
                <div style="font-size:48px">{icon}</div>

                <div style="
                    font-size:23px;
                    font-weight:bold;
                    color:#70243f;
                ">
                    {html.escape(LEVELS[i][0])}
                </div>

                <div style="font-size:20px;color:#70243f">
                    {['Rất dễ', 'Dễ', 'Trung bình', 'Khó', 'Rất khó'][i]}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if done:
                st.markdown(
                    "<p style='text-align:center;font-size:18px'>"
                    "Đã hoàn thành</p>",
                    unsafe_allow_html=True
                )

            if st.button(
                "Chơi màn này" if unlocked else "Đã khóa",
                key=f"level_{i}",
                disabled=not unlocked,
                use_container_width=True
            ):
                st.session_state.level = i
                st.session_state.puzzle = make_puzzle(i)
                st.session_state.board = [
                    row[:] for row in st.session_state.puzzle
                ]
                st.session_state.status = "playing"

                go("game")

    st.write("")

    if st.button("← Về menu", use_container_width=True):
        go("menu")


# =========================
# GAME SUDOKU
# =========================

elif st.session_state.page == "game":

    inject_background(ASSETS / "game_bg.png")

    level = st.session_state.level

    st.markdown(
        f"<h1 style='text-align:center;color:#e52f79'>"
        f"{html.escape(LEVELS[level][0])}</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p class='subtitle'>"
        "Mỗi hàng, cột và khối 3×3 cần đủ số từ 1 đến 9."
        "</p>",
        unsafe_allow_html=True
    )

    puzzle = st.session_state.p
