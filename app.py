import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import random
import html

st.set_page_config(
    page_title="Sudoku Sakura",
    page_icon="🌸",
    layout="wide",
)

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

# =========================
# BẢNG SUDOKU MẪU
# =========================

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

DIFFICULTIES = [
    "Rất dễ",
    "Dễ",
    "Trung bình",
    "Khó",
    "Rất khó",
]

# =========================
# TẠO CÂU ĐỐ
# =========================

def make_puzzle(level):
    keep = LEVELS[level][1]

    cells = [
        (r, c)
        for r in range(9)
        for c in range(9)
    ]

    random.Random(2026 + level).shuffle(cells)

    puzzle = [
        row[:]
        for row in SOLUTION
    ]

    for r, c in cells[:81 - keep]:
        puzzle[r][c] = 0

    return puzzle


# =========================
# ĐỌC ẢNH VÀ ÂM THANH
# =========================

def data_uri(path):
    if not path.is_file():
        return ""

    extension = path.suffix.lower()

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }

    mime = mime_types.get(extension, "image/png")

    encoded = base64.b64encode(
        path.read_bytes()
    ).decode("ascii")

    return f"data:{mime};base64,{encoded}"


def audio_uri(filename):
    path = ASSETS / filename

    if not path.is_file():
        return None

    encoded = base64.b64encode(
        path.read_bytes()
    ).decode("ascii")

    return f"data:audio/mpeg;base64,{encoded}"


def play_effect(kind):
    filenames = {
        "click": "sounds_click.mp3",
        "win": "sounds_win.mp3",
        "lose": "sounds_lose.mp3",
    }

    filename = filenames.get(kind)

    if not filename:
        return

    src = audio_uri(filename)

    if src:
        components.html(
            f"""
            <audio autoplay>
                <source src="{src}" type="audio/mpeg">
            </audio>
            """,
            height=0,
        )


# =========================
# HIỆU ỨNG HOA ANH ĐÀO RƠI
# =========================

PETALS = """
<style>
.sakura-petal {
    position: fixed;
    top: -60px;
    z-index: 999;
    pointer-events: none;
    user-select: none;
    opacity: 0.82;
    animation: sakura-fall linear infinite;
}

@keyframes sakura-fall {
    0% {
        transform: translateY(-5vh) rotate(0deg);
    }

    100% {
        transform: translateY(115vh) rotate(600deg);
    }
}
</style>

<div aria-hidden="true">
    <span class="sakura-petal"
        style="left:4%;font-size:23px;animation-duration:11s">
        🌸
    </span>

    <span class="sakura-petal"
        style="left:15%;font-size:18px;animation-duration:14s;animation-delay:2s">
        🌸
    </span>

    <span class="sakura-petal"
        style="left:29%;font-size:25px;animation-duration:12s;animation-delay:1s">
        🌸
    </span>

    <span class="sakura-petal"
        style="left:43%;font-size:18px;animation-duration:15s;animation-delay:4s">
        🌸
    </span>

    <span class="sakura-petal"
        style="left:58%;font-size:24px;animation-duration:13s;animation-delay:3s">
        🌸
    </span>

    <span class="sakura-petal"
        style="left:72%;font-size:20px;animation-duration:11s;animation-delay:1s">
        🌸
    </span>

    <span class="sakura-petal"
        style="left:86%;font-size:24px;animation-duration:14s;animation-delay:5s">
        🌸
    </span>

    <span class="sakura-petal"
        style="left:96%;font-size:17px;animation-duration:12s;animation-delay:2s">
        🌸
    </span>
</div>
"""


# =========================
# GIAO DIỆN CHUNG
# =========================

def inject_background(filename):
    uri = data_uri(ASSETS / filename)

    background_css = ""

    if uri:
        background_css = f"""
        background-image:
            linear-gradient(
                rgba(255, 242, 246, 0.28),
                rgba(255, 242, 246, 0.38)
            ),
            url("{uri}");
        """

    st.markdown(
        f"""
        <style>
        @import url(
            'https://fonts.googleapis.com/css2?family=Yeseva+One&display=swap'
        );

        html,
        body,
        [class*="st-"],
        button,
        input,
        label,
        p,
        h1,
        h2,
        h3,
        span,
        div {{
            font-family: 'Yeseva One', Georgia, serif !important;
        }}

        .stApp {{
            {background_css}
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #5C102C;
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        .block-container {{
            padding-top: 1.5rem;
            max-width: 1250px;
        }}

        h1 {{
            color: #8B123D;
            font-size: clamp(40px, 5vw, 60px) !important;
        }}

        h2 {{
            color: #8B123D;
            font-size: 38px !important;
        }}

        h3 {{
            color: #8B123D;
            font-size: 30px !important;
        }}

        p,
        label,
        [data-testid="stMarkdownContainer"] {{
            color: #5C102C;
            font-size: 20px;
            line-height: 1.55;
        }}

        .subtitle {{
            color: #6F1235;
            text-align: center;
            font-size: 23px;
            font-weight: bold;
        }}

        div.stButton > button {{
            color: #5C102C !important;
            background: #E8A0B5 !important;
            border: 2px solid #85143D !important;
            border-radius: 16px !important;
            min-height: 54px;
            font-size: 20px !important;
            font-weight: bold !important;
            box-shadow: 0 4px 12px rgba(92, 16, 44, 0.16);
        }}

        div.stButton > button:hover {{
            background: #C6537A !important;
            color: #FFFFFF !important;
            border-color: #6F1235 !important;
        }}

        div.stButton > button:disabled {{
            background: #D7B4C0 !important;
            color: #80616D !important;
            border-color: #B88A9A !important;
        }}

        div[data-baseweb="select"] > div {{
            background: #FFF4F7;
            border-color: #85143D;
            color: #5C102C;
            min-height: 45px;
        }}

        [data-testid="stAlert"] {{
            background: rgba(255, 246, 249, 0.96);
            border: 1px solid #9E1748;
            color: #5C102C;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# KHỞI TẠO SESSION
# =========================

defaults = {
    "page": "menu",
    "level": 0,
    "unlocked": 0,
    "completed": [],
    "status": "playing",
    "board": None,
    "puzzle": None,
    "last_effect": None,
}

for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default


def go(page):
    st.session_state.page = page
    st.rerun()


def start_level(level):
    st.session_state.level = level

    puzzle = make_puzzle(level)

    st.session_state.puzzle = [
        row[:]
        for row in puzzle
    ]

    st.session_state.board = [
        row[:]
        for row in puzzle
    ]

    st.session_state.status = "playing"
    st.session_state.last_effect = None

    go("game")


def ensure_game_state():
    level = st.session_state.get("level", 0)

    if not isinstance(level, int) or not 0 <= level < len(LEVELS):
        level = 0
        st.session_state.level = level

    puzzle = st.session_state.get("puzzle")
    board = st.session_state.get("board")

    if (
        not isinstance(puzzle, list)
        or len(puzzle) != 9
        or not isinstance(board, list)
        or len(board) != 9
    ):
        puzzle = make_puzzle(level)

        st.session_state.puzzle = [
            row[:]
            for row in puzzle
        ]

        st.session_state.board = [
            row[:]
            for row in puzzle
        ]

        st.session_state.status = "playing"

    return (
        st.session_state["puzzle"],
        st.session_state["board"],
    )


# =========================
# MENU CHÍNH
# =========================

if st.session_state.page == "menu":

    menu_uri = data_uri(ASSETS / "menu.png")

    menu_background = ""

    if menu_uri:
        menu_background = f"""
        background-image:
            linear-gradient(
                rgba(255, 244, 248, 0.10),
                rgba(255, 244, 248, 0.10)
            ),
            url("{menu_uri}");
        """

    st.markdown(
        f"""
        <style>
        @import url(
            'https://fonts.googleapis.com/css2?family=Yeseva+One&display=swap'
        );

        html,
        body,
        [class*="st-"],
        button,
        p,
        h1,
        div {{
            font-family: 'Yeseva One', Georgia, serif !important;
        }}

        .stApp {{
            {menu_background}
            background-size: cover !important;
            background-position: center center !important;
            background-attachment: fixed !important;
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        .block-container {{
            padding-top: 1rem;
            max-width: 1200px;
        }}

        .menu-title {{
            text-align: center;
            font-size: clamp(90px, 13vw, 165px);
            line-height: 1.2;
            font-weight: 900;
            color: #8B123D;
            -webkit-text-stroke: 1px #F5D3DF;
            text-shadow:
                0 3px 0 #F5D3DF,
                0 8px 25px rgba(75, 5, 30, 0.4);
            margin: 0 auto;
        }}

        div.stButton > button {{
            color: #5C102C !important;
            background: linear-gradient(
                145deg,
                #F0B2C5,
                #C6537A
            ) !important;
            border: 4px solid #85143D !important;
            border-radius: 50% !important;
            width: 220px !important;
            height: 220px !important;
            min-height: 220px !important;
            white-space: pre-line !important;
            font-size: 30px !important;
            line-height: 1.35 !important;
            font-weight: bold !important;
            box-shadow:
                0 0 0 9px rgba(255, 239, 246, 0.75),
                0 10px 28px rgba(92, 16, 44, 0.32);
            transition: transform 0.2s ease;
        }}

        div.stButton > button:hover {{
            background: linear-gradient(
                145deg,
                #D97798,
                #9E1748
            ) !important;
            color: #FFFFFF !important;
            transform: scale(1.05);
        }}
        </style>

        <h1 class="menu-title">Sudoku</h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(PETALS, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:22px;
            color:#6F1235;
            font-weight:bold;
