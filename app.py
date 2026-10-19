
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
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

WINE = "#781638"
ROSE = "#C65D7B"
PALE = "#FCE8EE"
DARK = "#421021"

LEVELS = [
    {"name": "Màn 1 · Cánh hoa", "clues": 38},
    {"name": "Màn 2 · Cành đào", "clues": 32},
    {"name": "Màn 3 · Vườn xuân", "clues": 28},
    {"name": "Màn 4 · Mưa hoa", "clues": 24},
    {"name": "Màn 5 · Sakura", "clues": 20},
]

# Đáp án Sudoku hợp lệ
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
# 2. ĐỌC TỆP ẢNH VÀ ÂM THANH
# =========================================================

def read_asset(filename):
    path = ASSETS / filename
    if path.exists():
        return path.read_bytes()
    return None


def image_as_base64(filename):
    data = read_asset(filename)
    if data is None:
        return None
    return base64.b64encode(data).decode("utf-8")


def play_sound(filename):
    """Phát âm thanh một lần khi có sự kiện."""
    data = read_asset(filename)
    if data is None:
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
    encoded = image_as_base64(filename)

    if encoded:
        css = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image:
                linear-gradient(
                    rgba(255, 247, 249, 0.28),
                    rgba(255, 247, 249, 0.28)
                ),
                url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """
    else:
        css = """
        <style>
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top, #fff2f5, #f8dce5);
        }
        </style>
        """

    st.markdown(css, unsafe_allow_html=True)


# =========================================================
# 3. TẠO BÀN CỜ
# =========================================================

def make_puzzle(level):
    """Tạo câu đố từ đáp án cố định, với số ô gợi ý theo cấp độ."""
    puzzle = [row[:] for row in SOLUTION]
    clues = LEVELS[level]["clues"]

    positions = [(r, c) for r in range(9) for c in range(9)]
    random.Random(100 + level).shuffle(positions)

    blanks = 81 - clues
    for r, c in positions[:blanks]:
        puzzle[r][c] = 0

    return puzzle


def start_level(level):
    st.session_state.level = level
    st.session_state.puzzle = make_puzzle(level)
    st.session_state.board = [
        row[:] for row in st.session_state.puzzle
    ]
    st.session_state.page = "game"
    st.session_state.status = "playing"
    st.session_state.sound_event = "click"

    # Xóa lựa chọn cũ để tránh giữ số của màn trước
    for r in range(9):
        for c in range(9):
            key = f"cell_{r}_{c}"
            if key in st.session_state:
                del st.session_state[key]


def find_conflicts(board, r, c, value):
    """Kiểm tra trùng số trên hàng, cột và khối 3×3."""
    for i in range(9):
        if i != c and board[r][i] == value:
            return True
        if i != r and board[i][c] == value:
            return True

    box_r = (r // 3) * 3
    box_c = (c // 3) * 3

    for rr in range(box_r, box_r + 3):
        for cc in range(box_c, box_c + 3):
            if (rr, cc) != (r, c) and board[rr][cc] == value:
                return True

    return False


def is_complete(board):
    return all(board[r][c] != 0 for r in range(9) for c in range(9))


def is_correct_solution(board):
    return board == SOLUTION


# =========================================================
# 4. TRẠNG THÁI TRÒ CHƠI
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
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# 5. GIAO DIỆN VÀ HIỆU ỨNG
# =========================================================

st.markdown(
    f"""
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=Yeseva+One&family=Nunito:wght@400;600;700;800&display=swap'
    );

    html, body, [class*="css"] {{
        font-family: 'Nunito', sans-serif;
    }}

    [data-testid="stAppViewContainer"] {{
        color: {DARK};
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    #MainMenu, footer {{
        visibility: hidden;
    }}

    .block-container {{
        max-width: 1180px;
        padding-top: 1.4rem;
        padding-bottom: 6rem;
    }}

    h1, h2, h3 {{
        color: {WINE};
    }}

    .sudoku-logo {{
        text-align: center;
        font-family: 'Yeseva One', serif;
        font-size: clamp(4rem, 11vw, 8rem);
        font-weight: 400;
        letter-spacing: 0.04em;
        color: {WINE};
        text-shadow:
            0 2px 0 #f6c5d2,
            0 6px 20px rgba(120, 22, 56, 0.18);
        animation: shimmer 3s ease-in-out infinite;
        margin: 2rem 0 0.3rem 0;
    }}

    @keyframes shimmer {{
        0%, 100% {{
            text-shadow:
                0 2px 0 #f6c5d2,
                0 6px 20px rgba(120, 22, 56, 0.18);
        }}
        50% {{
            text-shadow:
                0 2px 0 #f6c5d2,
                0 0 24px rgba(198, 93, 123, 0.48);
        }}
    }}

    .subtitle {{
        text-align: center;
        color: {WINE};
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0.4rem 0 1.4rem 0;
    }}

    .section-title {{
        text-align: center;
        font-family: 'Yeseva One', serif;
        color: {WINE};
        font-size: clamp(2rem, 4vw, 3.5rem);
        margin: 0.8rem 0 1.5rem 0;
    }}

    .hint {{
        text-align: center;
        font-size: 1.1rem;
        color: {WINE};
        font-weight: 800;
        margin-top: 0.8rem;
    }}

    div.stButton > button {{
        background: {WINE};
        color: white;
        border: 2px solid #e6a7b9;
        border-radius: 18px;
        min-height: 3.2rem;
        font-weight: 800;
        font-size: 1.05rem;
        transition: 0.2s ease;
        box-shadow: 0 5px 14px rgba(120, 22, 56, 0.12);
    }}

    div.stButton > button:hover {{
        background: {ROSE};
        color: white;
        border-color: {WINE};
        transform: translateY(-2px);
    }}

    div.stButton > button:focus {{
        box-shadow: 0 0 0 3px #f5c8d5;
        color: white;
    }}

    .level-note {{
        text-align: center;
        color: {WINE};
        font-size: 1.1rem;
        font-weight: 800;
        margin-bottom: 1.6rem;
    }}

    .board-shell {{
        max-width: 650px;
        margin: 0 auto;
        padding: 10px;
        border: 3px solid {WINE};
        border-radius: 20px;
        background: rgba(255, 242, 246, 0.8);
        box-shadow: 0 10px 30px rgba(120, 22, 56, 0.12);
    }}

    .block-label {{
        color: {WINE};
        font-size: 0.9rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.3rem;
    }}

    div[data-testid="stSelectbox"] {{
        min-width: 0;
    }}

    div[data-testid="stSelectbox"] label {{
        display: none;
    }}

    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
        min-height: 2.55rem;
        background: #fff7f9;
        border-color: #d98ca4;
        border-radius: 8px;
    }}

    div[data-testid="stSelectbox"] [data-baseweb="select"] {{
        font-weight: 800;
        color: {WINE};
    }}

    .status-box {{
        text-align: center;
        padding: 1rem;
        color: {WINE};
        font-size: 1.2rem;
        font-weight: 800;
        border: 1px solid #e5a9bb;
        border-radius: 16px;
        background: rgba(255, 241, 246, 0.85);
        margin: 1rem 0;
    }}

    .petal {{
        position: fixed;
        top: -40px;
        z-index: 999;
        pointer-events: none;
        color: #e78da9;
        opacity: 0.65;
        animation: fall linear infinite;
    }}

    @keyframes fall {{
        0% {{
            transform: translate3d(0, -10vh, 0) rotate(0deg);
        }}
        100% {{
            transform: translate3d(70px, 115vh, 0) rotate(540deg);
        }}
    }}

    [data-testid="stIFrame"] {{
        border: 0;
    }}

    @media (max-width: 700px) {{
        .block-container {{
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }}

        div[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
            min-height: 2.1rem;
        }}
    }}
    </style>

    <div class="petal" style="left:5%;animation-duration:12s;">✿</div>
    <div class="petal" style="left:16%;animation-duration:17s;animation-delay:2s;">❀</div>
    <div class="petal" style="left:29%;animation-duration:14s;animation-delay:4s;">✿</div>
    <div class="petal" style="left:43%;animation-duration:19s;animation-delay:1s;">❀</div>
    <div class="petal" style="left:57%;animation-duration:13s;animation-delay:3s;">✿</div>
    <div class="petal" style="left:70%;animation-duration:16s;animation-delay:5s;">❀</div>
    <div class="petal" style="left:84%;animation-duration:15s;animation-delay:2s;">✿</div>
    <div class="petal" style="left:94%;animation-duration:18s;animation-delay:6s;">❀</div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 6. NHẠC NỀN
# =========================================================

music_data = read_asset("sounds_bgm.mp3")

if music_data and st.session_state.music_on:
    music_encoded = base64.b64encode(music_data).decode("utf-8")

    st.markdown(
        f"""
        <style>
        .music-player {{
            position: fixed;
            left: 8px;
            bottom: 8px;
            width: 260px;
            z-index: 9999;
            padding: 7px;
            border: 1px solid #d98ca4;
            border-radius: 14px;
            background: rgba(255, 240, 245, 0.96);
            box-shadow: 0 4px 15px rgba(120, 22, 56, 0.18);
        }}

        .music-player audio {{
            width: 100%;
            height: 32px;
        }}
        </style>

        <div class="music-player">
          <audio controls loop autoplay>
            <source
              src="data:audio/mpeg;base64,{music_encoded}"
              type="audio/mpeg">
          </audio>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Phát hiệu ứng âm thanh đã được kích hoạt từ lượt trước
event = st.session_state.sound_event

if event:
    sound_files = {
        "click": "sounds_click.mp3",
        "lose": "sounds_lose.mp3",
        "win": "sounds_win.mp3",
    }
    if event in sound_files:
        play_sound(sound_files[event])
    st.session_state.sound_event = None


# =========================================================
# 7. CHUYỂN TRANG
# =========================================================

def go(page):
    st.session_state.sound_event = "click"
    st.session_state.page = page
    st.rerun()


# =========================================================
# 8. TRANG CHỦ
# =========================================================

if st.session_state.page == "menu":
    show_background("menu.png")

    st.markdown(
        '<div class="sudoku-logo">Sudoku</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">✧ Sakura Edition ✧</div>',
        unsafe_allow_html=True,
    )

    flower = image_as_base64("menu.png")

    left, center, right = st.columns([1, 1.1, 1])

    with center:
        if flower:
            st.markdown(
                f"""
                <div style="text-align:center;">
                    <img
                      src="data:image/png;base64,{flower}"
                      style="width:100%;max-width:280px;
                             max-height:260px;object-fit:contain;
                             border-radius:24px;"
                    >
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("🌸", key="flower_start", use_container_width=True):
            go("levels")

        st.markdown(
            '<div class="hint">Ấn vào bông hoa để bắt đầu</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button(
            "♪  Bật / tắt nhạc nền",
            key="toggle_music",
            use_container_width=True,
        ):
            st.session_state.music_on = not st.session_state.music_on
            st.session_state.sound_event = "click"
            st.rerun()


# =========================================================
# 9. TRANG CHỌN CẤP ĐỘ
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

        col1, col2 = st.columns([3, 1])

        with col1:
            if completed:
                label = f"🌸  {level['name']}  ·  Đã hoàn thành"
            elif unlocked:
                label = f"🌸  {level['name']}"
            else:
                label = f"🔒  {level['name']}  ·  Chưa mở khóa"

            st.markdown(
                f"""
                <div style="
                    color:{WINE};
                    font-size:1.35rem;
                    font-weight:800;
                    padding:0.6rem 0;
                ">{label}</div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
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

    st.write("")

    if st.button("← Quay về trang chủ", key="back_menu"):
        go("menu")


# =========================================================
# 10. TRANG CHƠI SUDOKU
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

        if st.button("← Quay lại chọn màn", key="lost_levels"):
            go("levels")

        if st.button("Về trang chủ", key="lost_home"):
            go("menu")

    elif st.session_state.status == "won":
        st.markdown(
            '<div class="status-box">'
            '🌸 Chúc mừng! Bạn đã hoàn thành màn chơi! 🌸'
            '</div>',
            unsafe_allow_html=True,
        )

        if st.button("Chọn màn tiếp theo →", key="next_level"):
            if level_index < len(LEVELS) - 1:
                start_level(level_index + 1)
                st.rerun()
            else:
                go("levels")

        if st.button("Về trang chọn màn", key="won_levels"):
            go("levels")

    else:
        board = st.session_state.board
        puzzle = st.session_state.puzzle

        st.markdown(
            '<div class="board-shell">',
            unsafe_allow_html=True,
        )

        # Mỗi khối 3×3 được đặt trong một container riêng.
        # Không mở/đóng thẻ HTML xuyên qua nhiều widget Streamlit.
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

                    # Container có viền tạo ranh giới cho khối 3×3.
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
                                                min-height:2.35rem;
                                                display:flex;
                                                justify-content:center;
                                                align-items:center;
                                                background:#f3d6e0;
                                                color:{WINE};
                                                border:1px solid #d98ca4;
                                                border-radius:8px;
                                                font-size:1.1rem;
                                                font-weight:900;
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
                                            if selected != "—" else 0
                                        )

                                        if value != board[r][c]:
                                            if value == 0:
                                                board[r][c] = 0
                                                st.rerun()

                                            # Kiểm tra luật Sudoku trước.
                                            if find_conflicts(
                                                board, r, c, value
                                            ):
                                                st.session_state.status = "lost"
                                                st.session_state.sound_event = "lose"
                                                st.rerun()

                                            # Kiểm tra đáp án ẩn để phát hiện
                                            # số không đúng ngay khi nhập.
                                            if value != SOLUTION[r][c]:
                                                st.session_state.status = "lost"
                                                st.session_state.sound_event = "lose"
                                                st.rerun()

                                            board[r][c] = value
                                            st.session_state.board = board

                                            if is_complete(board):
                                                if is_correct_solution(board):
                                                    st.session_state.status = "won"
                                                    st.session_state.sound_event = "win"

                                                    if level_index not in st.session_state.completed:
                                                        st.session_state.completed.append(level_index)

                                                    st.session_state.unlocked = max(
                                                        st.session_state.unlocked,
                                                        min(level_index + 1, len(LEVELS) - 1),
                                                    )
                                                else:
                                                    st.session_state.status = "lost"
                                                    st.session_state.sound_event = "lose"

                                            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button(
                "← Chọn màn khác",
                key="game_levels",
                use_container_width=True,
            ):
                go("levels")

        with col_b:
            if st.button(
                "⌂ Trang chủ",
                key="game_home",
                use_container_width=True,
            ):
                go("menu")
