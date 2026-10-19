
import base64
import random
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# =========================================================
# 1. CẤU HÌNH
# =========================================================

st.set_page_config(
    page_title="Sudoku Sakura",
    page_icon="🌸",
    layout="wide",
)

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

WINE = "#781638"
ROSE = "#C65D7B"
DARK = "#421021"

LEVELS = [
    {"name": "Màn 1 · Cánh hoa", "clues": 38},
    {"name": "Màn 2 · Cành đào", "clues": 32},
    {"name": "Màn 3 · Vườn xuân", "clues": 28},
    {"name": "Màn 4 · Mưa hoa", "clues": 24},
    {"name": "Màn 5 · Sakura", "clues": 20},
]

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


# =========================================================
# 2. TỆP ASSETS VÀ ÂM THANH
# =========================================================

def read_asset(filename):
    path = ASSETS / filename
    return path.read_bytes() if path.exists() else None


def asset_b64(filename):
    data = read_asset(filename)
    return base64.b64encode(data).decode("utf-8") if data else None


def play_sound(filename):
    data = read_asset(filename)
    if not data:
        return

    encoded = base64.b64encode(data).decode("utf-8")
    components.html(
        f"""
        <audio autoplay>
            <source src="data:audio/mpeg;base64,{encoded}"
                    type="audio/mpeg">
        </audio>
        """,
        height=0,
    )


def show_background(filename):
    encoded = asset_b64(filename)

    if encoded:
        background = (
            "background-image: "
            "linear-gradient(rgba(255,247,249,.22),"
            "rgba(255,247,249,.22)),"
            f'url("data:image/png;base64,{encoded}");'
        )
    else:
        background = (
            "background: linear-gradient(135deg,#fff0f4,#f4d2df);"
        )

    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            {background}
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 3. TRẠNG THÁI TRÒ CHƠI
# =========================================================

DEFAULTS = {
    "page": "menu",
    "level": 0,
    "unlocked": 0,
    "completed": [],
    "status": "playing",
    "puzzle": None,
    "board": None,
    "sound_event": None,
    "music_on": True,
    "celebrated": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def go(page):
    st.session_state.sound_event = "click"
    st.session_state.page = page
    st.rerun()


def make_puzzle(level):
    puzzle = [row[:] for row in SOLUTION]
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.Random(100 + level).shuffle(positions)

    for r, c in positions[:81 - LEVELS[level]["clues"]]:
        puzzle[r][c] = 0

    return puzzle


def start_level(level):
    for r in range(9):
        for c in range(9):
            key = f"cell_{r}_{c}"
            if key in st.session_state:
                del st.session_state[key]

    st.session_state.level = level
    st.session_state.puzzle = make_puzzle(level)
    st.session_state.board = [
        row[:] for row in st.session_state.puzzle
    ]
    st.session_state.status = "playing"
    st.session_state.page = "game"
    st.session_state.sound_event = "click"
    st.session_state.celebrated = False


def has_conflict(board, r, c, value):
    for i in range(9):
        if i != c and board[r][i] == value:
            return True
        if i != r and board[i][c] == value:
            return True

    start_r = (r // 3) * 3
    start_c = (c // 3) * 3

    for rr in range(start_r, start_r + 3):
        for cc in range(start_c, start_c + 3):
            if (rr, cc) != (r, c) and board[rr][cc] == value:
                return True

    return False


def board_complete(board):
    return all(board[r][c] != 0 for r in range(9) for c in range(9))


# =========================================================
# 4. CSS — GIỮ NGUYÊN MÀU SẮC, SỬA HOA VÀ CĂN GIỮA
# =========================================================

st.markdown(
    f"""
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=Yeseva+One&display=swap'
    );

    html, body, *,
    [class*="css"],
    button, input, textarea, select,
    [data-baseweb],
    [data-testid="stMarkdownContainer"] {{
        font-family: 'Yeseva One', serif !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    #MainMenu, footer {{
        visibility: hidden;
    }}

    .block-container {{
        max-width: 1200px;
        padding-top: 1rem;
        padding-bottom: 8rem;
    }}

    /* TIÊU ĐỀ */
    .sudoku-logo {{
        text-align: center;
        width: 100%;
        color: {WINE};
        font-size: clamp(2rem, 5.5vw, 5.5rem);
        line-height: 1.35;
        margin: 1.2rem 0 1rem;
        text-shadow: 0 3px 0 #f4c2d1,
                     0 8px 25px rgba(120,22,56,.24);
        animation: logoGlow 3s ease-in-out infinite;
        white-space: nowrap;
    }}

    @keyframes logoGlow {{
        0%, 100% {{
            text-shadow: 0 3px 0 #f4c2d1,
                         0 8px 25px rgba(120,22,56,.24);
        }}
        50% {{
            text-shadow: 0 3px 0 #f4c2d1,
                         0 0 32px rgba(198,93,123,.65);
        }}
    }}

    .subtitle {{
        width: 100%;
        text-align: center;
        color: {WINE};
        font-size: 1.5rem;
        margin-bottom: 0;
    }}

    .hint {{
        width: 100%;
        text-align: center;
        color: {WINE};
        font-size: 1.3rem;
        margin-top: 0.5rem;
    }}

    .section-title {{
        text-align: center;
        font-size: clamp(2rem, 5vw, 4rem);
        color: {WINE};
        margin: 1rem 0 1.5rem;
    }}

    .level-note {{
        text-align: center;
        color: {WINE};
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
    }}

    /* ==================================================
       HOA ANH ĐÀO:
       - CĂN GIỮA TOÀN BỘ MÀN HÌNH
       - PHÓNG TO BIỂU TƯỢNG HOA, KHÔNG PHÓNG TO CÁI Ô
       - NỀN NÚT TRONG SUỐT
       ================================================== */

    .st-key-flower_start {{
        position: relative !important;

        /* Mở rộng vùng chứa ra đúng chiều ngang viewport */
        width: 100vw !important;
        max-width: 100vw !important;

        /* Đưa tâm vùng chứa trùng với tâm màn hình */
        left: 50% !important;
        transform: translateX(-50%) !important;

        display: flex !important;
        justify-content: center !important;
        align-items: center !important;

        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }}

    .st-key-flower_start > div {{
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        overflow: visible !important;
    }}

    .st-key-flower_start .st-key-flower_button {{
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        overflow: visible !important;
    }}

    .st-key-flower_start button {{
        /* Kích thước nằm ở CHỮ HOA, không phải kích thước ô */
        font-family:
            "Segoe UI Emoji",
            "Apple Color Emoji",
            "Noto Color Emoji",
            sans-serif !important;

        font-size: clamp(15rem, 28vw, 24rem) !important;
        line-height: 1 !important;

        width: auto !important;
        min-width: 0 !important;
        max-width: none !important;
        height: auto !important;
        min-height: 0 !important;

        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;

        padding: 0 !important;
        margin: 0 auto !important;

        color: inherit !important;
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        border-radius: 0 !important;

        cursor: pointer !important;
        overflow: visible !important;
        transition: transform .25s ease !important;
    }}

    .st-key-flower_start button p {{
        font-family:
            "Segoe UI Emoji",
            "Apple Color Emoji",
            "Noto Color Emoji",
            sans-serif !important;
        font-size: inherit !important;
        line-height: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    .st-key-flower_start button:hover,
    .st-key-flower_start button:focus,
    .st-key-flower_start button:active {{
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }}

    .st-key-flower_start button:hover {{
        transform: scale(1.04) rotate(-4deg) !important;
    }}

    /* NÚT THƯỜNG */
    div.stButton > button {{
        background: {WINE};
        color: white !important;
        border: 2px solid #e7a8ba;
        border-radius: 18px;
        min-height: 3.2rem;
        font-size: 1.1rem !important;
        padding: .6rem 1rem;
        transition: .2s ease;
    }}

    div.stButton > button:hover {{
        background: {ROSE};
        color: white !important;
        border-color: {WINE};
        transform: translateY(-2px);
    }}

    .block-label {{
        text-align: center;
        color: {WINE};
        font-size: 1rem;
        margin-bottom: .3rem;
    }}

    [data-testid="stSelectbox"] label {{
        display: none;
    }}

    [data-testid="stSelectbox"] [data-baseweb="select"] > div {{
        min-height: 2.5rem;
        background: #fff7f9;
        border-color: #d98ca4;
        border-radius: 8px;
    }}

    [data-testid="stSelectbox"] [data-baseweb="select"] * {{
        font-family: 'Yeseva One', serif !important;
        color: {WINE};
    }}

    .status-box {{
        text-align: center;
        padding: 1.2rem;
        color: {WINE};
        font-size: 1.4rem;
        border: 2px solid #e5a9bb;
        border-radius: 18px;
        background: rgba(255,241,246,.92);
        margin: 1rem 0;
    }}

    /* CÁNH HOA RƠI */
    .petal {{
        position: fixed;
        top: -100px;
        z-index: 999;
        pointer-events: none;
        color: #e7799b;
        opacity: .78;
        animation: petalFall linear infinite;
    }}

    @keyframes petalFall {{
        0% {{
            transform: translate3d(0,-10vh,0) rotate(0deg);
        }}
        50% {{
            transform: translate3d(80px,50vh,0) rotate(240deg);
        }}
        100% {{
            transform: translate3d(-45px,115vh,0) rotate(560deg);
        }}
    }}

    /* NÚT NHẠC ĐẶT GẦN GÓC TRÁI DƯỚI */
    .st-key-toggle_music {{
        position: fixed !important;
        left: 8px !important;
        bottom: 54px !important;
        width: 280px !important;
        z-index: 100001 !important;
    }}

    .st-key-toggle_music button {{
        width: 100% !important;
        min-height: 34px !important;
        padding: 5px 8px !important;
        margin: 0 !important;
        border-radius: 10px !important;
        font-size: .9rem !important;
    }}

    @media (max-width: 700px) {{
        .block-container {{
            padding-left: .5rem;
            padding-right: .5rem;
        }}

        .sudoku-logo {{
            font-size: clamp(1.5rem, 7vw, 3rem);
            white-space: normal;
        }}

        .st-key-flower_start button {{
            font-size: clamp(12rem, 48vw, 19rem) !important;
        }}

        .st-key-toggle_music {{
            width: 240px !important;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 5. HOA ANH ĐÀO RƠI
# =========================================================

random.seed(23)
petal_html = ""

for i in range(28):
    left = random.randint(0, 98)
    size = random.randint(24, 48)
    duration = random.randint(9, 20)
    delay = random.randint(0, 18)
    symbol = random.choice(["✿", "❀", "🌸", "✾"])

    petal_html += (
        f'<div class="petal" style="left:{left}%;'
        f'font-size:{size}px;animation-duration:{duration}s;'
        f'animation-delay:-{delay}s;">{symbol}</div>'
    )

st.markdown(petal_html, unsafe_allow_html=True)


# =========================================================
# 6. NHẠC NỀN
# =========================================================

music_data = read_asset("sounds_bgm.mp3")

if music_data:
    music_encoded = base64.b64encode(music_data).decode("utf-8")

    st.markdown(
        f"""
        <div style="
            position:fixed;
            left:0;
            bottom:0;
            width:300px;
            padding:8px;
            box-sizing:border-box;
            border:1px solid #d98ca4;
            border-radius:14px;
            background:rgba(255,240,245,.97);
            z-index:99999;
        ">
            <audio controls loop
                   {"autoplay" if st.session_state.music_on else ""}>
                <source src="data:audio/mpeg;base64,{music_encoded}"
                        type="audio/mpeg">
            </audio>
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.page == "menu":
    music_label = (
        "♪ Tắt nhạc nền"
        if st.session_state.music_on
        else "♪ Bật nhạc nền"
    )

    if st.button(music_label, key="toggle_music"):
        st.session_state.music_on = not st.session_state.music_on
        st.rerun()

if st.session_state.sound_event:
    sound_map = {
        "click": "sounds_click.mp3",
        "lose": "sounds_lose.mp3",
        "win": "sounds_win.mp3",
    }
    filename = sound_map.get(st.session_state.sound_event)

    if filename:
        play_sound(filename)

    st.session_state.sound_event = None


# =========================================================
# 7. MENU CHÍNH
# =========================================================

if st.session_state.page == "menu":
    show_background("menu.png")

    st.markdown(
        '<div class="sudoku-logo">'
        '˚₊‧꒰ა Sudoku ໒꒱ ‧₊˚'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">✧ Sakura Edition ✧</div>',
        unsafe_allow_html=True,
    )

    # Không dùng columns nữa: hoa được căn giữa theo viewport.
    with st.container(key="flower_start"):
        if st.button("🌸", key="flower_button"):
            go("levels")

    st.markdown(
        '<div class="hint">Ấn vào bông hoa để bắt đầu</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# 8. CHỌN MÀN CHƠI
# =========================================================

elif st.session_state.page == "levels":
    show_background("menu.png")

    st.markdown(
        '<div class="section-title">Chọn màn chơi</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="level-note">'
        'Hoàn thành từng màn để mở khóa màn tiếp theo 🌸'
        '</div>',
        unsafe_allow_html=True,
    )

    for i, level in enumerate(LEVELS):
        unlocked = i <= st.session_state.unlocked
        completed = i in st.session_state.completed

        left, right = st.columns([3, 1])

        with left:
            if completed:
                label = f"🌸 {level['name']} · Đã hoàn thành"
            elif unlocked:
                label = f"🌸 {level['name']}"
            else:
                label = f"🔒 {level['name']} · Chưa mở khóa"

            st.markdown(
                f"""
                <div style="
                    color:{WINE};
                    font-size:1.35rem;
                    padding:.7rem 0;
                ">{label}</div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            if unlocked:
                if st.button(
                    "Chơi ngay",
                    key=f"level_{i}",
                    use_container_width=True,
                ):
                    start_level(i)
                    st.rerun()
            else:
                st.button(
                    "Đã khóa",
                    key=f"locked_{i}",
                    disabled=True,
                    use_container_width=True,
                )

    if st.button("← Về trang chủ", key="back_menu"):
        go("menu")


# =========================================================
# 9. TRANG SUDOKU
# =========================================================

elif st.session_state.page == "game":
    show_background("game_bg.png")

    level_index = st.session_state.level
    level = LEVELS[level_index]

    st.markdown(
        f'<div class="section-title">{level["name"]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="level-note">'
        'Điền số từ 1 đến 9 vào các ô trống'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.status == "lost":
        st.markdown(
            '<div class="status-box">'
            'Bạn đã sai rồi, không có cơ hội chơi lại đâu nha'
            '</div>',
            unsafe_allow_html=True,
        )

        if st.button("← Chọn màn khác", key="lost_levels"):
            go("levels")

        if st.button("⌂ Về trang chủ", key="lost_home"):
            go("menu")

    elif st.session_state.status == "won":
        if not st.session_state.celebrated:
            st.balloons()
            st.session_state.celebrated = True

        st.markdown(
            '<div class="status-box">'
            '🌸 Chúc mừng! Bạn đã hoàn thành màn chơi! 🌸'
            '</div>',
            unsafe_allow_html=True,
        )

        if level_index < len(LEVELS) - 1:
            if st.button(
                "Chơi màn tiếp theo →",
                key="next_level",
                use_container_width=True,
            ):
                start_level(level_index + 1)
                st.rerun()

        if st.button("← Chọn màn khác", key="won_levels"):
            go("levels")

        if st.button("⌂ Về trang chủ", key="won_home"):
            go("menu")

    else:
        board = st.session_state.board
        puzzle = st.session_state.puzzle

        # Chín khối 3×3 được tách riêng
        for block_row in range(3):
            block_columns = st.columns(3, gap="medium")

            for block_col in range(3):
                with block_columns[block_col]:
                    st.markdown(
                        f'<div class="block-label">'
                        f'Khối {block_row * 3 + block_col + 1}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    with st.container(border=True):
                        for local_r in range(3):
                            r = block_row * 3 + local_r
                            cell_columns = st.columns(3, gap="small")

                            for local_c in range(3):
                                c = block_col * 3 + local_c

                                with cell_columns[local_c]:
                                    if puzzle[r][c] != 0:
                                        st.markdown(
                                            f"""
                                            <div style="
                                                min-height:2.5rem;
                                                display:flex;
                                                justify-content:center;
                                                align-items:center;
                                                background:#f3d6e0;
                                                color:{WINE};
                                                border:1px solid #d98ca4;
                                                border-radius:8px;
                                                font-size:1.1rem;
                                            ">{puzzle[r][c]}</div>
                                            """,
                                            unsafe_allow_html=True,
                                        )
                                    else:
                                        key = f"cell_{r}_{c}"
                                        options = ["—"] + [
                                            str(n) for n in range(1, 10)
                                        ]

                                        current = board[r][c]
                                        default_index = (
                                            options.index(str(current))
                                            if current else 0
                                        )

                                        selected = st.selectbox(
                                            f"Ô {r + 1}-{c + 1}",
                                            options,
                                            index=default_index,
                                            key=key,
                                            label_visibility="collapsed",
                                        )

                                        value = (
                                            int(selected)
                                            if selected != "—"
                                            else 0
                                        )

                                        if value != board[r][c]:
                                            if value == 0:
                                                board[r][c] = 0
                                                st.session_state.sound_event = None
                                                st.rerun()

                                            # Phát hiện đáp án sai
                                            if (
                                                has_conflict(board, r, c, value)
                                                or value != SOLUTION[r][c]
                                            ):
                                                st.session_state.status = "lost"
                                                st.session_state.sound_event = "lose"
                                                st.rerun()

                                            board[r][c] = value
                                            st.session_state.board = board
                                            st.session_state.sound_event = "win"

                                            if board_complete(board):
                                                if board == SOLUTION:
                                                    st.session_state.status = "won"

                                                    if level_index not in st.session_state.completed:
                                                        st.session_state.completed.append(
                                                            level_index
                                                        )

                                                    st.session_state.unlocked = max(
                                                        st.session_state.unlocked,
                                                        min(
                                                            level_index + 1,
                                                            len(LEVELS) - 1,
                                                        ),
                                                    )
                                                    st.session_state.celebrated = False
                                                else:
                                                    st.session_state.status = "lost"
                                                    st.session_state.sound_event = "lose"

                                            st.rerun()

        st.write("")
        left, right = st.columns(2)

        with left:
            if st.button(
                "← Chọn màn khác",
                key="game_levels",
                use_container_width=True,
            ):
                go("levels")

        with right:
            if st.button(
                "⌂ Về trang chủ",
                key="game_home",
                use_container_width=True,
            ):
                go("menu")
