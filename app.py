import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import random
import html

st.set_page_config(
    page_title="Sakura Sudoku",
    page_icon="🌸",
    layout="wide",
)

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

# =========================
# SUDOKU
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


def make_puzzle(level):
    keep = LEVELS[level][1]
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.Random(2026 + level).shuffle(cells)

    puzzle = [row[:] for row in SOLUTION]

    for r, c in cells[:81 - keep]:
        puzzle[r][c] = 0

    return puzzle


# =========================
# ẢNH VÀ ÂM THANH
# =========================

def data_uri(path):
    if not path.is_file():
        return ""

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }

    mime = mime_types.get(path.suffix.lower(), "image/png")
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

    src = audio_uri(files[kind])

    if src:
        components.html(
            f'<audio autoplay><source src="{src}" type="audio/mpeg"></audio>',
            height=0,
        )


# =========================
# HOA ANH ĐÀO RƠI
# =========================

PETALS = """
<style>
.sakura-petal {
    position: fixed;
    top: -60px;
    z-index: 999;
    pointer-events: none;
    user-select: none;
    opacity: 0.85;
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
          style="left:4%;font-size:23px;animation-duration:11s">🌸</span>
    <span class="sakura-petal"
          style="left:15%;font-size:18px;animation-duration:14s;animation-delay:2s">🌸</span>
    <span class="sakura-petal"
          style="left:29%;font-size:25px;animation-duration:12s;animation-delay:1s">🌸</span>
    <span class="sakura-petal"
          style="left:43%;font-size:18px;animation-duration:15s;animation-delay:4s">🌸</span>
    <span class="sakura-petal"
          style="left:58%;font-size:24px;animation-duration:13s;animation-delay:3s">🌸</span>
    <span class="sakura-petal"
          style="left:72%;font-size:20px;animation-duration:11s;animation-delay:1s">🌸</span>
    <span class="sakura-petal"
          style="left:86%;font-size:24px;animation-duration:14s;animation-delay:5s">🌸</span>
    <span class="sakura-petal"
          style="left:96%;font-size:17px;animation-duration:12s;animation-delay:2s">🌸</span>
</div>
"""


# =========================
# CSS GIAO DIỆN CHUNG
# =========================

def inject_background(filename):
    uri = data_uri(ASSETS / filename)
    background_css = ""

    if uri:
        background_css = f"""
        background-image:
            linear-gradient(
                rgba(255, 242, 246, 0.25),
                rgba(255, 242, 246, 0.35)
            ),
            url("{uri}");
        """

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Yeseva+One&display=swap');

        html, body, [class*="st-"], button, input, label,
        p, h1, h2, h3, span, div {{
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

        h1, h2, h3 {{
            color: #8B123D;
        }}

        h1 {{
            font-size: clamp(40px, 5vw, 60px) !important;
        }}

        p, label, [data-testid="stMarkdownContainer"] {{
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
            color: white !important;
            border-color: #6F1235 !important;
        }}

        div.stButton > button:disabled {{
            background: #D7B4C0 !important;
            color: #80616D !important;
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
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# SESSION STATE
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

    st.session_state.puzzle = [row[:] for row in puzzle]
    st.session_state.board = [row[:] for row in puzzle]
    st.session_state.status = "playing"
    st.session_state.last_effect = None

    go("game")


def ensure_game_state():
    level = st.session_state.get("level", 0)

    if not isinstance(level, int) or not 0 <= level < len(LEVELS):
        level = 0
        st.session_state.level = 0

    puzzle = st.session_state.get("puzzle")
    board = st.session_state.get("board")

    valid_puzzle = (
        isinstance(puzzle, list)
        and len(puzzle) == 9
        and all(isinstance(row, list) and len(row) == 9 for row in puzzle)
    )

    valid_board = (
        isinstance(board, list)
        and len(board) == 9
        and all(isinstance(row, list) and len(row) == 9 for row in board)
    )

    if not valid_puzzle or not valid_board:
        puzzle = make_puzzle(level)

        st.session_state.puzzle = [row[:] for row in puzzle]
        st.session_state.board = [row[:] for row in puzzle]
        st.session_state.status = "playing"

    return st.session_state["puzzle"], st.session_state["board"]


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
        @import url('https://fonts.googleapis.com/css2?family=Yeseva+One&display=swap');

        html, body, [class*="st-"], button, p, h1, div {{
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
            background: linear-gradient(145deg, #F0B2C5, #C6537A) !important;
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
            background: linear-gradient(145deg, #D97798, #9E1748) !important;
            color: white !important;
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
        <p style="
            text-align:center;
            font-size:22px;
            color:#6F1235;
            font-weight:bold;
        ">
            🌸 Welcome to Sakura Sudoku 🌸
        </p>
        """,
        unsafe_allow_html=True,
    )

    music_src = audio_uri("sounds_bgm.mp3")

    if music_src:
        st.markdown(
            f"""
            <div style="
                max-width:340px;
                margin:14px auto 0;
                text-align:center;
                color:#5C102C;
                font-size:18px;
                font-weight:bold;
            ">
                🌸 Nhạc nền — nhấn Play để bật
                <audio controls loop preload="auto"
                    style="display:block;width:100%;margin-top:8px">
                    <source src="{music_src}" type="audio/mpeg">
                </audio>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("Không tìm thấy assets/sounds_bgm.mp3.")

    st.markdown("<div style='height:5vh'></div>", unsafe_allow_html=True)

    left, center, right = st.columns([1, 1, 1])

    with center:
        if st.button(
            "🌸\nPLAY NOW\n🌸",
            key="start_game",
            use_container_width=True,
        ):
            go("levels")


# =========================
# CHỌN MÀN CHƠI
# =========================

elif st.session_state.page == "levels":
    inject_background("game_bg.png")
    st.markdown(PETALS, unsafe_allow_html=True)

    st.markdown(
        """
        <h1 style="text-align:center;color:#8B123D;font-size:55px">
            Chọn màn chơi
        </h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="subtitle">Chọn một khu vườn để bắt đầu 🌸</p>',
        unsafe_allow_html=True,
    )

    columns = st.columns(5, gap="medium")

    for i, col in enumerate(columns):
        with col:
            unlocked = i <= st.session_state.unlocked
            done = i in st.session_state.completed
            icon = "🌸" if done else ("🔓" if unlocked else "🔒")

            st.markdown(
                f"""
                <div style="text-align:center;padding:10px 2px;min-height:135px">
                    <div style="font-size:45px">{icon}</div>
                    <div style="font-size:21px;font-weight:bold;color:#6F1235">
                        {html.escape(LEVELS[i][0])}
                    </div>
                    <div style="font-size:18px;color:#5C102C">
                        {DIFFICULTIES[i]}
                    </div>
                    <div style="font-size:15px;color:#85143D">
                        {"Đã hoàn thành" if done else ""}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Chơi màn này" if unlocked else "Đã khóa",
                key=f"level_{i}",
                disabled=not unlocked,
                use_container_width=True,
            ):
                start_level(i)

    if st.button("← Về menu", use_container_width=True):
        go("menu")


# =========================
# MÀN CHƠI SUDOKU
# =========================

elif st.session_state.page == "game":
    inject_background("game_bg.png")
    st.markdown(PETALS, unsafe_allow_html=True)

    puzzle, board = ensure_game_state()
    level = st.session_state.level

    st.markdown(
        f"""
        <h1 style="text-align:center;color:#8B123D">
            {html.escape(LEVELS[level][0])}
        </h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p class="subtitle">
            Mỗi hàng, cột và khối 3×3 cần đủ số từ 1 đến 9.
        </p>
        """,
        unsafe_allow_html=True,
    )

    for block_row in range(3):
        block_columns = st.columns(3, gap="small")

        for block_col in range(3):
            with block_columns[block_col]:
                st.markdown(
                    """
                    <div style="
                        background:rgba(255,246,249,0.88);
                        border:2px solid #85143D;
                        border-radius:9px;
                        padding:5px;
                    ">
                    """,
                    unsafe_allow_html=True,
                )

                for r in range(block_row * 3, block_row * 3 + 3):
                    cells = st.columns(3, gap="small")

                    for c in range(block_col * 3, block_col * 3 + 3):
                        with cells[c % 3]:
                            if puzzle[r][c] != 0:
                                st.markdown(
                                    f"""
                                    <div style="
                                        height:45px;
                                        display:flex;
                                        align-items:center;
                                        justify-content:center;
                                        background:#E8A0B5;
                                        border:1px solid #85143D;
                                        border-radius:5px;
                                        font-weight:bold;
                                        font-size:22px;
                                        color:#5C102C;
                                    ">
                                        {puzzle[r][c]}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            else:
                                options = ["—"] + [
                                    str(n) for n in range(1, 10)
                                ]

                                current_value = board[r][c]
                                current = (
                                    str(current_value)
                                    if current_value
                                    else "—"
                                )

                                selected = st.selectbox(
                                    f"Ô {r + 1}-{c + 1}",
                                    options,
                                    index=options.index(current),
                                    key=f"cell_{level}_{r}_{c}",
                                    label_visibility="collapsed",
                                    disabled=(
                                        st.session_state.status != "playing"
                                    ),
                                )

                                value = 0 if selected == "—" else int(selected)

                                if value != board[r][c]:
                                    board[r][c] = value

                                    if value and value != SOLUTION[r][c]:
                                        st.session_state.status = "lost"

                                    elif all(
                                        board[rr][cc] == SOLUTION[rr][cc]
                                        for rr in range(9)
                                        for cc in range(9)
                                    ):
                                        st.session_state.status = "won"

                                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

    status = st.session_state.status

    if status == "lost":
        if st.session_state.last_effect != "lose":
            play_effect("lose")
            st.session_state.last_effect = "lose"

        st.error("🍂 Bạn đã điền sai số. Hãy thử lại nhé!")

        left, right = st.columns(2)

        with left:
            if st.button("🔄 Chơi lại", use_container_width=True):
                start_level(level)

        with right:
            if st.button("🌸 Chọn màn khác", use_container_width=True):
                go("levels")

    elif status == "won":
        if st.session_state.last_effect != "win":
            play_effect("win")
            st.session_state.last_effect = "win"

        st.success("🌸 Tuyệt vời! Bạn đã hoàn thành màn chơi!")

        if level not in st.session_state.completed:
            st.session_state.completed.append(level)

        st.session_state.unlocked = max(
            st.session_state.unlocked,
            min(4, level + 1),
        )

        if level < 4:
            if st.button("➡️ Sang màn tiếp theo", use_container_width=True):
                start_level(level + 1)
        else:
            st.balloons()
            st.markdown(
                """
                <h2 style="text-align:center;color:#85143D">
                    🏆 Bạn đã chinh phục cả 5 màn Sudoku!
                </h2>
                """,
                unsafe_allow_html=True,
            )

        if st.button("Chọn màn chơi", use_container_width=True):
            go("levels")

    else:
        if st.button("🏠 Về chọn màn", use_container_width=True):
            go("levels")
```
