import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import random
import html

st.set_page_config(
    page_title="Sudoku",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

WINE = "#781638"
DARK_WINE = "#511027"
ROSE = "#C6537A"
PALE_ROSE = "#F8DCE6"

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

DIFFICULTIES = ["Rất dễ", "Dễ", "Trung bình", "Khó", "Rất khó"]


# -------------------- TÀI NGUYÊN --------------------

def data_uri(path):
    if not path.is_file():
        return ""

    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(path.suffix.lower(), "application/octet-stream")

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def audio_uri(filename):
    path = ASSETS / filename
    if not path.is_file():
        return ""

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:audio/mpeg;base64,{encoded}"


def make_puzzle(level):
    """Tạo bảng có các ô trống dựa trên một bảng Sudoku hợp lệ."""
    keep = LEVELS[level][1]
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.Random(2026 + level).shuffle(cells)

    puzzle = [row[:] for row in SOLUTION]

    for r, c in cells[:81 - keep]:
        puzzle[r][c] = 0

    return puzzle


def reset_game(level):
    puzzle = make_puzzle(level)

    st.session_state.level = level
    st.session_state.puzzle = puzzle
    st.session_state.board = [row[:] for row in puzzle]
    st.session_state.status = "playing"
    st.session_state.invalid_move = False


def go(page):
    st.session_state.page = page
    st.rerun()


# -------------------- LUẬT SUDOKU CHUẨN --------------------

def get_conflicts(board):
    """
    Trả về các ô có số trùng trong hàng, cột hoặc khối 3x3.
    Không so sánh với đáp án bí mật.
    """
    conflicts = set()

    for r in range(9):
        for c in range(9):
            value = board[r][c]

            if value == 0:
                continue

            # Kiểm tra hàng ngang
            for other_c in range(9):
                if other_c != c and board[r][other_c] == value:
                    conflicts.add((r, c))
                    conflicts.add((r, other_c))

            # Kiểm tra cột dọc
            for other_r in range(9):
                if other_r != r and board[other_r][c] == value:
                    conflicts.add((r, c))
                    conflicts.add((other_r, c))

            # Kiểm tra khối 3x3
            start_r = (r // 3) * 3
            start_c = (c // 3) * 3

            for rr in range(start_r, start_r + 3):
                for cc in range(start_c, start_c + 3):
                    if (rr, cc) != (r, c) and board[rr][cc] == value:
                        conflicts.add((r, c))
                        conflicts.add((rr, cc))

    return conflicts


def board_is_complete(board):
    return all(board[r][c] != 0 for r in range(9) for c in range(9))


def board_is_valid(board):
    if not board_is_complete(board):
        return False

    if get_conflicts(board):
        return False

    required = set(range(1, 10))

    for r in range(9):
        if set(board[r]) != required:
            return False

    for c in range(9):
        if {board[r][c] for r in range(9)} != required:
            return False

    for start_r in (0, 3, 6):
        for start_c in (0, 3, 6):
            block = {
                board[r][c]
                for r in range(start_r, start_r + 3)
                for c in range(start_c, start_c + 3)
            }
            if block != required:
                return False

    return True


# -------------------- TRẠNG THÁI --------------------

defaults = {
    "page": "menu",
    "level": 0,
    "unlocked": 0,
    "completed": [],
    "status": "playing",
    "board": None,
    "puzzle": None,
    "invalid_move": False,
    "music_enabled": True,
}

for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default


# -------------------- GIAO DIỆN CHUNG --------------------

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Yeseva+One&display=swap');

    html, body, [class*="st-"], button, input, label,
    p, h1, h2, h3, span, div, textarea {{
        font-family: 'Yeseva One', Georgia, serif !important;
    }}

    .stApp {{
        color: {WINE};
        background-color: #FFF4F7;
        background-size: cover !important;
        background-position: center center !important;
        background-attachment: fixed !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stToolbar"] {{
        right: 1rem;
    }}

    .block-container {{
        max-width: 1250px;
        padding-top: 1.2rem;
        padding-bottom: 7rem;
    }}

    h1, h2, h3, p, label {{
        color: {WINE};
    }}

    .subtitle {{
        text-align: center;
        color: {WINE};
        font-size: 22px;
        margin-bottom: 22px;
    }}

    .menu-title {{
        text-align: center;
        font-size: clamp(120px, 17vw, 230px);
        line-height: 1.12;
        font-weight: 900;
        letter-spacing: 1px;
        color: #781638 !important;
        -webkit-text-fill-color: #781638;
        -webkit-text-stroke: 0;
        text-shadow: 0 5px 0 rgba(255, 226, 236, .8),
                     0 12px 28px rgba(81, 16, 39, .16);
        margin: 10px auto 0;
    }}

    .play-flower {{
        text-align: center;
        font-size: clamp(70px, 9vw, 115px);
        line-height: 1;
        margin-top: 4px;
        transform: translateX(28px);
        filter: drop-shadow(0 5px 8px rgba(81, 16, 39, .18));
    }}

    .play-label {{
        text-align: center;
        font-size: clamp(42px, 5.5vw, 68px);
        color: {WINE};
        font-weight: 900;
        letter-spacing: 3px;
        line-height: 1.1;
        transform: translateX(28px);
        text-shadow: 0 3px 0 #F8DCE6;
        margin-top: 10px;
        margin-bottom: 5px;
    }}

    div.stButton > button {{
        color: {WINE} !important;
        background: linear-gradient(145deg, #FFF0F5, #E8A0B5) !important;
        border: 2px solid #B64A70 !important;
        border-radius: 16px !important;
        min-height: 52px;
        font-size: 20px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 12px rgba(81, 16, 39, .10);
        transition: transform .18s ease, background .18s ease;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(145deg, #FFE3ED, #D87998) !important;
        transform: translateY(-2px);
        border-color: {DARK_WINE} !important;
    }}

    div.stButton > button:disabled {{
        background: rgba(235, 216, 223, .65) !important;
        color: #9B8490 !important;
        border-color: #D5B9C4 !important;
    }}

    div[data-baseweb="select"] > div {{
        background: rgba(255, 248, 250, .96);
        border-color: #BD6686;
        color: {WINE};
        min-height: 42px;
    }}

    [data-testid="stAlert"] {{
        background: rgba(255, 249, 251, .96);
        border: 1px solid #D990A6;
        color: {WINE};
    }}

    .level-name {{
        color: {WINE};
        text-align: center;
        font-size: 21px;
        line-height: 1.4;
        margin-top: 8px;
        min-height: 60px;
    }}

    .petal {{
        position: fixed;
        top: -60px;
        z-index: 999;
        pointer-events: none;
        user-select: none;
        opacity: .78;
        animation: petal-fall linear infinite;
    }}

    @keyframes petal-fall {{
        0% {{ transform: translateY(-5vh) rotate(0deg); }}
        100% {{ transform: translateY(115vh) rotate(600deg); }}
    }}

    .sudoku-cell {{
        height: 43px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 5px;
        font-size: 22px;
        font-weight: bold;
        color: {WINE};
        background: rgba(255, 247, 250, .94);
        border: 1px solid #D9A0B4;
        margin-bottom: 3px;
    }}

    .fixed-cell {{
        background: rgba(239, 199, 213, .95);
        border-color: #C87591;
    }}

    .music-control {{
        position: fixed;
        left: 12px;
        bottom: 12px;
        width: min(330px, 82vw);
        z-index: 1000;
        background: rgba(255, 244, 248, .96);
        border: 1px solid #C87591;
        border-radius: 14px;
        padding: 8px 12px;
        box-shadow: 0 4px 18px rgba(81, 16, 39, .15);
        color: {WINE};
        font-size: 13px;
    }}

    .music-control audio {{
        display: block;
        width: 100%;
        height: 34px;
        margin-top: 3px;
    }}

    @media (max-width: 700px) {{
        .menu-title {{
            font-size: 22vw;
        }}
        .sudoku-cell {{
            height: 34px;
            font-size: 17px;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- CÁNH HOA RƠI --------------------

PETALS = """
<div aria-hidden="true">
<style>
.petal {
  position:fixed; top:-60px; z-index:999;
  pointer-events:none; user-select:none; opacity:.78;
  animation:petal-fall linear infinite;
}
@keyframes petal-fall {
  0% { transform:translateY(-5vh) rotate(0deg); }
  100% { transform:translateY(115vh) rotate(600deg); }
}
</style>
<span class="petal" style="left:5%;font-size:22px;animation-duration:10s">🌸</span>
<span class="petal" style="left:17%;font-size:17px;animation-duration:13s;animation-delay:2s">🌸</span>
<span class="petal" style="left:31%;font-size:23px;animation-duration:11s;animation-delay:1s">🌸</span>
<span class="petal" style="left:47%;font-size:18px;animation-duration:14s;animation-delay:4s">🌸</span>
<span class="petal" style="left:63%;font-size:22px;animation-duration:12s;animation-delay:3s">🌸</span>
<span class="petal" style="left:78%;font-size:19px;animation-duration:10s;animation-delay:1s">🌸</span>
<span class="petal" style="left:92%;font-size:24px;animation-duration:15s;animation-delay:5s">🌸</span>
</div>
"""


def set_background(filename):
    uri = data_uri(ASSETS / filename)
    if uri:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image:
                    linear-gradient(
                        rgba(255, 244, 248, .25),
                        rgba(255, 244, 248, .30)
                    ),
                    url("{uri}");
                background-size: cover !important;
                background-position: center !important;
                background-attachment: fixed !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )


def show_music():
    src = audio_uri("sounds_bgm.mp3")

    if not src:
        return

    if st.session_state.music_enabled:
        music_html = f"""
        <div class="music-control">
          <div><b>🌸 Nhạc nền Sakura</b></div>
          <audio controls loop preload="auto">
            <source src="{src}" type="audio/mpeg">
          </audio>
        </div>
        """
    else:
        music_html = """
        <div class="music-control">
          <b>🌸 Nhạc nền đang tắt</b>
        </div>
        """

    components.html(music_html, height=75, scrolling=False)


def play_effect(kind):
    filename = {
        "click": "sounds_click.mp3",
        "win": "sounds_win.mp3",
        "lose": "sounds_lose.mp3",
    }.get(kind, "sounds_click.mp3")

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


# -------------------- MENU CHÍNH --------------------

if st.session_state.page == "menu":
    set_background("menu.png")

    st.markdown(
        '<h1 class="menu-title">Sudoku</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(PETALS, unsafe_allow_html=True)

    st.markdown("<div style='height:5vh'></div>", unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.25, 1])

    with center:
        st.markdown(
            '<div class="play-label">PLAY NOW</div>'
            '<div class="play-flower">🌸</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "BẮT ĐẦU CHƠI",
            key="start_game",
            use_container_width=True,
        ):
            play_effect("click")
            go("levels")

    st.markdown(
        """
        <p style="text-align:center;font-size:18px;margin-top:20px">
        Một khu vườn Sudoku đang chờ bạn khám phá 🌸
        </p>
        """,
        unsafe_allow_html=True,
    )

    music_src = audio_uri("sounds_bgm.mp3")

    if not music_src:
        st.warning(
            "Chưa tìm thấy assets/sounds_bgm.mp3. "
            "Hãy kiểm tra tên file nhạc nền."
        )

    show_music()


# -------------------- CHỌN MÀN --------------------

elif st.session_state.page == "levels":
    set_background("game_bg.png")
    st.markdown(PETALS, unsafe_allow_html=True)

    st.markdown(
        f"""
        <h1 style="
            text-align:center;
            color:{WINE};
            font-size:clamp(42px,6vw,66px);
        ">Chọn màn chơi</h1>
        <p class="subtitle">Chọn một khu vườn để bắt đầu 🌸</p>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(5, gap="medium")

    for i, col in enumerate(cols):
        with col:
            unlocked = i <= st.session_state.unlocked
            done = i in st.session_state.completed

            icon = "🌸" if done else ("🔓" if unlocked else "🔒")

            st.markdown(
                f"""
                <div style="text-align:center;padding:8px 2px">
                  <div style="font-size:48px">{icon}</div>
                  <div class="level-name">
                    {html.escape(LEVELS[i][0])}
                  </div>
                  <div style="
                    text-align:center;
                    color:{WINE};
                    font-size:18px;
                    margin-bottom:10px;
                  ">{DIFFICULTIES[i]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if done:
                st.markdown(
                    f"""
                    <p style="text-align:center;color:{WINE};font-size:15px">
                    Đã hoàn thành ✓
                    </p>
                    """,
                    unsafe_allow_html=True,
                )

            label = "Chơi màn này" if unlocked else "Đã khóa"

            if st.button(
                label,
                key=f"level_{i}",
                disabled=not unlocked,
                use_container_width=True,
            ):
                play_effect("click")
                reset_game(i)
                go("game")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if st.button("← Về menu", use_container_width=True):
        play_effect("click")
        go("menu")

    show_music()


# -------------------- MÀN CHƠI SUDOKU --------------------

elif st.session_state.page == "game":
    set_background("game_bg.png")
    st.markdown(PETALS, unsafe_allow_html=True)

    level = st.session_state.level
    puzzle = st.session_state.puzzle
    board = st.session_state.board

    if puzzle is None or board is None:
        reset_game(level)
        st.rerun()

    st.markdown(
        f"""
        <h1 style="
            text-align:center;
            color:{WINE};
            font-size:clamp(38px,5vw,58px);
        ">{html.escape(LEVELS[level][0])}</h1>
        <p class="subtitle">
        Mỗi hàng, cột và khối 3×3 phải có đủ số từ 1 đến 9,
        không được trùng lặp.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Hiển thị bảng 9x9 thành 9 khối 3x3.
    for block_row in range(3):
        block_columns = st.columns(3, gap="small")

        for block_col in range(3):
            with block_columns[block_col]:
                for r in range(block_row * 3, block_row * 3 + 3):
                    cells = st.columns(3, gap="small")

                    for c in range(block_col * 3, block_col * 3 + 3):
                        with cells[c % 3]:
                            if puzzle[r][c] != 0:
                                st.markdown(
                                    f"""
                                    <div class="sudoku-cell fixed-cell">
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
                                current_text = (
                                    str(current_value)
                                    if current_value
                                    else "—"
                                )

                                widget_key = f"cell_{level}_{r}_{c}"

                                # Khởi tạo lựa chọn ban đầu.
                                if widget_key not in st.session_state:
                                    st.session_state[widget_key] = current_text

                                selected = st.selectbox(
                                    f"Ô {r + 1}-{c + 1}",
                                    options,
                                    key=widget_key,
                                    label_visibility="collapsed",
                                    disabled=st.session_state.status == "won",
                                )

                                value = (
                                    0 if selected == "—" else int(selected)
                                )

                                if value != board[r][c]:
                                    board[r][c] = value
                                    st.session_state.invalid_move = False

                                    # Chỉ kiểm tra trùng số theo luật Sudoku.
                                    conflicts = get_conflicts(board)

                                    if conflicts:
                                        st.session_state.invalid_move = True

                                    # Không bắt thua chỉ vì khác đáp án mẫu.
                                    if board_is_valid(board):
                                        st.session_state.status = "won"

                                    play_effect("click")

    conflicts = get_conflicts(st.session_state.board)

    if conflicts:
        st.warning(
            "🌸 Có số bị trùng trong hàng, cột hoặc khối 3×3. "
            "Bạn hãy sửa các ô đang trùng nhé. Bạn chưa thua!"
        )
    elif st.session_state.status != "won":
        st.info(
            "Điền số từ 1 đến 9. Nếu chưa đúng, bạn vẫn có thể sửa "
            "và tiếp tục chơi."
        )

    # -------------------- THẮNG MÀN --------------------

    if st.session_state.status == "won":
        play_effect("win")

        st.success(
            "🌸 Tuyệt vời! Bạn đã hoàn thành Sudoku hợp lệ!"
        )

        if level not in st.session_state.completed:
            st.session_state.completed.append(level)

        st.session_state.unlocked = max(
            st.session_state.unlocked,
            min(4, level + 1),
        )

        if level < 4:
            if st.button(
                "➡️ Sang màn tiếp theo",
                use_container_width=True,
            ):
                play_effect("click")
                reset_game(level + 1)
                go("game")
        else:
            st.balloons()
            st.markdown(
                f"""
                <h2 style="text-align:center;color:{WINE}">
                🏆 Bạn đã chinh phục cả 5 màn Sudoku!
                </h2>
                """,
                unsafe_allow_html=True,
            )

        if st.button("🌸 Chọn màn chơi", use_container_width=True):
            play_effect("click")
            go("levels")

    # -------------------- ĐIỀU HƯỚNG --------------------

    else:
        left, right = st.columns(2)

        with left:
            if st.button("🔄 Chơi lại màn này", use_container_width=True):
                play_effect("click")
                reset_game(level)
                st.rerun()

        with right:
            if st.button("🌸 Chọn màn khác", use_container_width=True):
                play_effect("click")
                go("levels")

    show_music()
