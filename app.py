
import base64
import random
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# =========================================================
# CẤU HÌNH
# =========================================================

st.set_page_config(
    page_title="Sudoku 🌸",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ASSETS = Path(__file__).parent / "assets"

MENU_IMAGE = ASSETS / "menu.png"
GAME_IMAGE = ASSETS / "game_bg.png"
MUSIC_FILE = ASSETS / "sounds_bgm.mp3"
CLICK_SOUND = ASSETS / "sounds_click.mp3"
LOSE_SOUND = ASSETS / "sounds_lose.mp3"
WIN_SOUND = ASSETS / "sounds_win.mp3"

WINE = "#8F2948"
DARK_WINE = "#55182D"
ROSE = "#D987A0"
LIGHT_ROSE = "#F8E7EC"
CREAM = "#FFF8F5"

# Lời giải Sudoku chuẩn
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

LEVELS = {
    1: {"name": "Dễ dàng", "blanks": 25},
    2: {"name": "Thư giãn", "blanks": 35},
    3: {"name": "Thử thách", "blanks": 45},
    4: {"name": "Khó nhằn", "blanks": 52},
    5: {"name": "Bậc thầy", "blanks": 58},
}

# =========================================================
# TIỆN ÍCH
# =========================================================

def file_data_uri(path):
    """Đọc file và chuyển thành data URI để nhúng vào HTML/CSS."""
    if not path.exists():
        return None

    suffix = path.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
    }
    mime = mime_types.get(suffix, "application/octet-stream")

    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def play_effect(sound_name):
    """Phát hiệu ứng âm thanh một lần."""
    sound_paths = {
        "click": CLICK_SOUND,
        "lose": LOSE_SOUND,
        "win": WIN_SOUND,
    }
    sound_path = sound_paths.get(sound_name)

    if sound_path and sound_path.exists():
        audio_uri = file_data_uri(sound_path)
        components.html(
            f"""
            <audio autoplay>
                <source src="{audio_uri}" type="audio/mpeg">
            </audio>
            """,
            height=0,
        )


def make_puzzle(level):
    """Tạo bảng Sudoku từ lời giải và số lượng ô trống theo cấp độ."""
    puzzle = [row[:] for row in SOLUTION]
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.Random(level * 137).shuffle(cells)

    blanks = LEVELS[level]["blanks"]

    for r, c in cells[:blanks]:
        puzzle[r][c] = 0

    return puzzle


def reset_game(level):
    """Khởi tạo ván mới."""
    puzzle = make_puzzle(level)

    st.session_state.level = level
    st.session_state.puzzle = [row[:] for row in puzzle]
    st.session_state.board = [row[:] for row in puzzle]
    st.session_state.selected_cell = None
    st.session_state.status = "playing"
    st.session_state.last_effect = None


def go(page, sound=True):
    if sound:
        play_effect("click")
    st.session_state.page = page


def board_is_complete():
    board = st.session_state.board
    return all(board[r][c] != 0 for r in range(9) for c in range(9))


def play_music_player():
    """Trình phát nhạc có nút phát/tạm dừng và thanh tua."""
    if not MUSIC_FILE.exists():
        return

    music_uri = file_data_uri(MUSIC_FILE)

    components.html(
        f"""
        <div style="
            position:fixed;
            bottom:12px;
            left:12px;
            width:310px;
            max-width:calc(100vw - 24px);
            z-index:999999;
            padding:10px;
            border-radius:16px;
            background:rgba(255,248,245,0.96);
            border:1px solid #D987A0;
            box-shadow:0 4px 18px rgba(85,24,45,0.20);
            box-sizing:border-box;
        ">
            <div style="
                color:#8F2948;
                font-family:Georgia,serif;
                font-size:13px;
                font-weight:bold;
                margin-bottom:5px;
            ">🌸 Sakura Music</div>
            <audio controls loop preload="metadata"
                style="width:100%;height:34px;">
                <source src="{music_uri}" type="audio/mpeg">
            </audio>
        </div>
        """,
        height=0,
    )


# =========================================================
# KHỞI TẠO SESSION
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "menu"

if "unlocked" not in st.session_state:
    st.session_state.unlocked = 1

if "level" not in st.session_state:
    st.session_state.level = 1

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "selected_cell" not in st.session_state:
    st.session_state.selected_cell = None

if "last_effect" not in st.session_state:
    st.session_state.last_effect = None

if "board" not in st.session_state:
    reset_game(1)


# =========================================================
# CSS GIAO DIỆN
# =========================================================

menu_bg = file_data_uri(MENU_IMAGE)
game_bg = file_data_uri(GAME_IMAGE)

background_css = ""

if st.session_state.page == "menu" and menu_bg:
    background_css = f"""
        background-image:linear-gradient(
            rgba(255,248,245,0.18),
            rgba(255,235,241,0.28)
        ), url("{menu_bg}");
    """
elif st.session_state.page != "menu" and game_bg:
    background_css = f"""
        background-image:linear-gradient(
            rgba(255,248,245,0.78),
            rgba(255,238,243,0.84)
        ), url("{game_bg}");
    """

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Yeseva+One&display=swap');

    :root {{
        --wine: {WINE};
        --dark-wine: {DARK_WINE};
        --rose: {ROSE};
        --light-rose: {LIGHT_ROSE};
        --cream: {CREAM};
    }}

    html, body, [class*="css"] {{
        font-family:'Yeseva One', serif !important;
    }}

    .stApp {{
        {background_css}
        background-size:cover;
        background-position:center;
        background-attachment:fixed;
    }}

    [data-testid="stHeader"] {{
        background:transparent;
    }}

    [data-testid="stSidebar"] {{
        background:#FFF0F3;
    }}

    h1, h2, h3, p, label, div, span {{
        font-family:'Yeseva One', serif;
    }}

    h1, h2, h3 {{
        color:var(--dark-wine);
    }}

    .main .block-container {{
        padding-top:1.5rem;
        padding-bottom:6rem;
        max-width:1200px;
    }}

    .sakura-title {{
        text-align:center;
        color:#9C3455;
        font-size:clamp(3.5rem, 9vw, 7rem);
        font-weight:normal;
        line-height:1.2;
        margin-top:5vh;
        margin-bottom:12px;
        text-shadow:
            0 2px 0 #FFF7F7,
            0 5px 18px rgba(110,25,53,0.24);
        animation:title-shimmer 3s ease-in-out infinite;
    }}

    @keyframes title-shimmer {{
        0%, 100% {{
            text-shadow:0 2px 0 #FFF7F7,
                0 5px 18px rgba(110,25,53,0.24);
        }}
        50% {{
            text-shadow:0 2px 0 white,
                0 0 24px rgba(196,91,126,0.75);
        }}
    }}

    .sakura-instruction {{
        text-align:center;
        font-size:clamp(1rem, 2vw, 1.35rem);
        color:#6B2039;
        margin-top:8px;
        margin-bottom:20px;
    }}

    /* Cánh hoa rơi */
    .petal {{
        position:fixed;
        top:-12vh;
        z-index:0;
        pointer-events:none;
        color:#D66F91;
        opacity:0.72;
        font-size:25px;
        animation:petal-fall linear infinite;
        text-shadow:0 1px 4px rgba(143,41,72,0.15);
    }}

    @keyframes petal-fall {{
        0% {{
            transform:translate3d(0,-10vh,0) rotate(0deg);
        }}
        50% {{
            transform:translate3d(55px,50vh,0) rotate(180deg);
        }}
        100% {{
            transform:translate3d(-25px,110vh,0) rotate(360deg);
        }}
    }}

    .petal-1 {{left:4%; animation-duration:13s; animation-delay:-2s;}}
    .petal-2 {{left:12%; animation-duration:17s; animation-delay:-8s; font-size:32px;}}
    .petal-3 {{left:21%; animation-duration:14s; animation-delay:-5s;}}
    .petal-4 {{left:32%; animation-duration:19s; animation-delay:-12s; font-size:30px;}}
    .petal-5 {{left:43%; animation-duration:12s; animation-delay:-6s;}}
    .petal-6 {{left:54%; animation-duration:18s; animation-delay:-3s; font-size:34px;}}
    .petal-7 {{left:65%; animation-duration:15s; animation-delay:-9s;}}
    .petal-8 {{left:74%; animation-duration:20s; animation-delay:-11s; font-size:31px;}}
    .petal-9 {{left:83%; animation-duration:14s; animation-delay:-4s;}}
    .petal-10 {{left:93%; animation-duration:17s; animation-delay:-7s; font-size:33px;}}
    .petal-11 {{left:17%; animation-duration:21s; animation-delay:-14s;}}
    .petal-12 {{left:48%; animation-duration:16s; animation-delay:-10s;}}
    .petal-13 {{left:78%; animation-duration:22s; animation-delay:-16s;}}
    .petal-14 {{left:37%; animation-duration:19s; animation-delay:-13s;}}
    .petal-15 {{left:88%; animation-duration:13s; animation-delay:-5s;}}

    /* Nút bấm */
    .stButton > button {{
        font-family:'Yeseva One', serif !important;
        color:var(--dark-wine) !important;
        background:rgba(255,248,245,0.94) !important;
        border:1.5px solid #D987A0 !important;
        border-radius:14px !important;
        min-height:44px;
        transition:all .2s ease;
        box-shadow:0 2px 7px rgba(85,24,45,0.07);
    }}

    .stButton > button:hover {{
        color:white !important;
        background:var(--wine) !important;
        border-color:var(--wine) !important;
        transform:translateY(-1px);
        box-shadow:0 5px 14px rgba(85,24,45,0.18);
    }}

    /* Nút hoa ở menu */
    div[class*="sakura-menu-button"] button {{
        background:rgba(255,248,245,0.16) !important;
        border:0 !important;
        box-shadow:none !important;
        font-size:clamp(7rem, 17vw, 13rem) !important;
        min-height:220px !important;
        line-height:1.1 !important;
        padding:0 !important;
        width:100% !important;
        animation:flower-float 3s ease-in-out infinite;
    }}

    div[class*="sakura-menu-button"] button:hover {{
        background:rgba(255,248,245,0.22) !important;
        transform:scale(1.06);
        box-shadow:0 0 30px rgba(205,105,139,0.25) !important;
    }}

    @keyframes flower-float {{
        0%, 100% {{ transform:translateY(0); }}
        50% {{ transform:translateY(-8px); }}
    }}

    /* Khung trò chơi */
    .game-heading {{
        text-align:center;
        color:#8F2948;
        font-size:clamp(2rem, 5vw, 3.4rem);
        margin-bottom:8px;
    }}

    .game-subheading {{
        text-align:center;
        color:#6B2039;
        margin-bottom:20px;
    }}

    .notice-box {{
        background:rgba(255,248,245,0.95);
        border:1px solid #D987A0;
        border-radius:16px;
        padding:14px 18px;
        color:#6B2039;
        text-align:center;
        margin:12px 0;
    }}

    /* Tạo viền phân chia từng ô Sudoku 3x3 */
    div[class*="sudoku-cell-"] {{
        padding:0 !important;
        margin:0 !important;
        border-right:1px solid rgba(143,41,72,0.15);
        border-bottom:1px solid rgba(143,41,72,0.15);
    }}

    div[class*="sudoku-cell-"] button {{
        width:100%;
        min-height:43px !important;
        height:43px !important;
        padding:0 !important;
        margin:0 !important;
        border-radius:0 !important;
        font-size:clamp(0.9rem, 2vw, 1.2rem) !important;
        background:rgba(255,252,250,0.97) !important;
        border:1px solid #E6C3CE !important;
        box-shadow:none !important;
    }}

    div[class*="sudoku-cell-"] button:hover {{
        background:#F4D4DF !important;
        color:#6B2039 !important;
    }}

    div[class*="sudoku-cell-fixed"] button {{
        background:#F4E4E8 !important;
        color:#6B2039 !important;
        font-weight:bold !important;
    }}

    div[class*="sudoku-cell-selected"] button {{
        background:#D987A0 !important;
        color:white !important;
        border:2px solid #8F2948 !important;
    }}

    div[class*="sudoku-cell-right"] {{
        border-right:3px solid #8F2948 !important;
    }}

    div[class*="sudoku-cell-bottom"] {{
        border-bottom:3px solid #8F2948 !important;
    }}

    .level-card {{
        text-align:center;
        background:rgba(255,248,245,0.92);
        border:1px solid #D987A0;
        border-radius:16px;
        padding:16px 8px;
        margin:8px 0;
        color:#6B2039;
    }}

    [data-testid="stProgressBar"] > div > div {{
        background-color:#A43B5C;
    }}

    /* Giữ nội dung trên lớp cánh hoa */
    [data-testid="stAppViewContainer"] {{
        position:relative;
    }}

    @media (max-width:600px) {{
        .main .block-container {{
            padding-left:0.45rem;
            padding-right:0.45rem;
        }}
        div[class*="sudoku-cell-"] button {{
            min-height:34px !important;
            height:34px !important;
            font-size:0.85rem !important;
        }}
    }}
    </style>

    <div aria-hidden="true">
        <span class="petal petal-1">🌸</span>
        <span class="petal petal-2">🌸</span>
        <span class="petal petal-3">🌸</span>
        <span class="petal petal-4">🌸</span>
        <span class="petal petal-5">🌸</span>
        <span class="petal petal-6">🌸</span>
        <span class="petal petal-7">🌸</span>
        <span class="petal petal-8">🌸</span>
        <span class="petal petal-9">🌸</span>
        <span class="petal petal-10">🌸</span>
        <span class="petal petal-11">🌸</span>
        <span class="petal petal-12">🌸</span>
        <span class="petal petal-13">🌸</span>
        <span class="petal petal-14">🌸</span>
        <span class="petal petal-15">🌸</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MENU CHÍNH
# =========================================================

if st.session_state.page == "menu":
    st.markdown('<div class="sakura-title">Sudoku</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="sakura-instruction">Ấn vào bông hoa để bắt đầu</div>',
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 1.5, 1])

    with center:
        with st.container(key="sakura-menu-button"):
            if st.button("🌸", key="sakura_start_button", use_container_width=True):
                play_effect("click")
                st.session_state.page = "levels"
                st.rerun()

    st.markdown(
        """
        <div class="notice-box">
            🌷 Một chút tập trung, một chút bình yên và thật nhiều niềm vui 🌷
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# CHỌN CẤP ĐỘ
# =========================================================

elif st.session_state.page == "levels":
    st.markdown('<div class="game-heading">Chọn cấp độ</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="game-subheading">Hoàn thành từng cấp để mở khóa cấp tiếp theo 🌸</div>',
        unsafe_allow_html=True,
    )

    if st.button("← Quay về trang chủ", key="back_to_menu"):
        play_effect("click")
        st.session_state.page = "menu"
        st.rerun()

    cols = st.columns(5)

    for level, col in zip(LEVELS.keys(), cols):
        info = LEVELS[level]
        unlocked = level <= st.session_state.unlocked

        with col:
            st.markdown(
                f"""
                <div class="level-card">
                    <div style="font-size:2rem;">{"🌸" if unlocked else "🔒"}</div>
                    <div style="font-size:1.15rem;">Cấp {level}</div>
                    <div style="font-size:0.9rem;">{info["name"]}</div>
                    <div style="font-size:0.8rem;">{info["blanks"]} ô trống</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if unlocked:
                if st.button("Bắt đầu", key=f"level_{level}", use_container_width=True):
                    play_effect("click")
                    reset_game(level)
                    st.session_state.page = "game"
                    st.rerun()
            else:
                st.button(
                    "Chưa mở khóa",
                    key=f"locked_{level}",
                    disabled=True,
                    use_container_width=True,
                )

    st.markdown(
        """
        <div class="notice-box">
            Mẹo nhỏ: Mỗi hàng, mỗi cột và mỗi ô vuông 3×3
            phải chứa các số từ 1 đến 9, không lặp lại.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# TRÒ CHƠI SUDOKU
# =========================================================

elif st.session_state.page == "game":
    level = st.session_state.level
    board = st.session_state.board
    puzzle = st.session_state.puzzle
    status = st.session_state.status

    st.markdown(
        f'<div class="game-heading">Sudoku 🌸</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="game-subheading">Cấp {level} · {LEVELS[level]["name"]}</div>',
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns([1, 1])

    with top_left:
        if st.button("← Chọn cấp độ", key="back_to_levels"):
            play_effect("click")
            st.session_state.page = "levels"
            st.rerun()

    with top_right:
        if st.button("↻ Chơi lại", key="restart_game"):
            play_effect("click")
            reset_game(level)
            st.rerun()

    if status == "lost":
        st.error("Bạn đã sai rồi, không có cơ hội chơi lại đâu nha 😭")
        st.markdown(
            """
            <div class="notice-box">
                🌸 Đừng buồn nhé! Hãy chọn lại cấp độ để thử sức lần nữa.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Chọn cấp độ khác", key="lost_back_levels"):
            play_effect("click")
            st.session_state.page = "levels"
            st.rerun()

    elif status == "won":
        st.success("Chúc mừng! Bạn đã hoàn thành Sudoku! 🎉")
        st.balloons()

        st.markdown(
            """
            <div class="notice-box">
                🌸 Tuyệt vời! Bạn đã giải xong bảng Sudoku này. 🌸
            </div>
            """,
            unsafe_allow_html=True,
        )

        if level < 5:
            if st.button(
                f"Mở khóa và chơi cấp {level + 1}",
                key="next_level",
                use_container_width=True,
            ):
                play_effect("click")
                st.session_state.unlocked = max(
                    st.session_state.unlocked, level + 1
                )
                reset_game(level + 1)
                st.session_state.page = "game"
                st.rerun()
        else:
            st.markdown(
                '<div class="notice-box">Bạn đã chinh phục cả 5 cấp độ! 👑</div>',
                unsafe_allow_html=True,
            )

        if st.button("Về chọn cấp độ", key="won_back_levels"):
            play_effect("click")
            st.session_state.page = "levels"
            st.rerun()

    else:
        filled = sum(
            1
            for r in range(9)
            for c in range(9)
            if board[r][c] != 0
        )
        progress = filled / 81

        st.progress(progress, text=f"Tiến độ: {filled}/81 ô")

        st.markdown(
            """
            <div class="notice-box">
                Chọn một ô trống, sau đó chọn số từ 1 đến 9.
                Nhập sai đáp án sẽ kết thúc lượt chơi.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Bảng Sudoku: 9 cột, phân chia đậm sau mỗi 3 cột và 3 hàng.
        for r in range(9):
            row_cols = st.columns(9, gap="small")

            for c in range(9):
                with row_cols[c]:
                    selected = st.session_state.selected_cell == (r, c)
                    fixed = puzzle[r][c] != 0

                    classes = [f"sudoku-cell-{r}-{c}"]

                    if fixed:
                        classes.append("sudoku-cell-fixed")
                    if selected:
                        classes.append("sudoku-cell-selected")
                    if c in (2, 5, 8):
                        classes.append("sudoku-cell-right")
                    if r in (2, 5, 8):
                        classes.append("sudoku-cell-bottom")

                    with st.container(key="-".join(classes)):
                        value = board[r][c]
                        label = str(value) if value else "·"

                        if st.button(
                            label,
                            key=f"cell_{r}_{c}",
                            disabled=fixed,
                            use_container_width=True,
                        ):
                            st.session_state.selected_cell = (r, c)
                            st.rerun()

        st.markdown(
            '<div class="game-subheading">Chọn số cần điền</div>',
            unsafe_allow_html=True,
        )

        number_cols = st.columns(9)

        for number, col in enumerate(number_cols, start=1):
            with col:
                if st.button(
                    str(number),
                    key=f"number_{number}",
                    use_container_width=True,
                ):
                    selected = st.session_state.selected_cell

                    if selected is None:
                        st.warning("Bạn hãy chọn một ô trống trước nhé!")
                    else:
                        r, c = selected

                        # Ô đã có sẵn không thể thay đổi.
                        if puzzle[r][c] != 0:
                            st.warning("Ô này không thể chỉnh sửa.")
                        elif number != SOLUTION[r][c]:
                            # Sai đáp án: phát âm thanh thua và khóa ván chơi.
                            st.session_state.board[r][c] = number
                            st.session_state.status = "lost"
                            st.session_state.last_effect = "lose"
                            play_effect("lose")
                            st.rerun()
                        else:
                            # Đáp án đúng.
                            st.session_state.board[r][c] = number
                            st.session_state.selected_cell = None

                            if board_is_complete():
                                st.session_state.status = "won"
                                st.session_state.last_effect = "win"
                                st.session_state.unlocked = max(
                                    st.session_state.unlocked,
                                    min(level + 1, 5),
                                )
                                play_effect("win")

                            st.rerun()

        if st.session_state.selected_cell is not None:
            r, c = st.session_state.selected_cell
            st.caption(f"Ô đang chọn: hàng {r + 1}, cột {c + 1}")


# =========================================================
# TRÌNH PHÁT NHẠC
# =========================================================

play_music_player()
