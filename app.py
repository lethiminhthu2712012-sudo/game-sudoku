
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import random
import html

st.set_page_config(
    page_title="game của thucute",
    page_icon="🌸",
    layout="wide",
)

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

# =========================
# DỮ LIỆU SUDOKU
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


def make_puzzle(level):
    """Tạo bảng Sudoku theo độ khó của từng màn."""
    keep = LEVELS[level][1]
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.Random(2026 + level).shuffle(cells)

    puzzle = [row[:] for row in SOLUTION]

    for r, c in cells[:81 - keep]:
        puzzle[r][c] = 0

    return puzzle


# =========================
# ẢNH NỀN VÀ ÂM THANH
# =========================

def data_uri(path):
    """Đọc ảnh và chuyển thành dữ liệu để hiển thị trong CSS."""
    if not path.is_file():
        return ""

    ext = path.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    mime = mime_types.get(ext, "image/png")

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def mp3_uri(filename):
    """Đọc file MP3 trong thư mục assets."""
    path = ASSETS / filename

    if not path.is_file():
        return None

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:audio/mpeg;base64,{encoded}"


def sound_html(kind="click", autoplay=True, loop=False):
    """Phát âm thanh tương ứng với thao tác trong game."""
    sound_files = {
        "click": "sounds_click.mp3",
        "place": "sounds_click.mp3",
        "win": "sounds_win.mp3",
        "lose": "sounds_lose.mp3",
        "music": "sounds_bgm.mp3",
    }

    filename = sound_files.get(kind, "sounds_click.mp3")
    src = mp3_uri(filename)

    if not src:
        return (
            f"<div style='color:#963e58;font-size:14px'>"
            f"Chưa tìm thấy {html.escape(filename)}"
            f"</div>"
        )

    autoplay_attr = "autoplay" if autoplay else ""
    loop_attr = "loop" if loop else ""

    return f"""
    <audio {autoplay_attr} {loop_attr}
        style="width:100%;max-width:320px">
        <source src="{src}" type="audio/mpeg">
        Trình duyệt không hỗ trợ MP3.
    </audio>
    """


def inject_background(path):
    """Giao diện nền dùng cho màn chọn màn và màn chơi."""
    uri = data_uri(path)

    background_css = ""
    if uri:
        background_css = f"""
        background-image:
            linear-gradient(
                rgba(255, 247, 249, 0.48),
                rgba(255, 247, 249, 0.58)
            ),
            url("{uri}");
        """

    st.markdown(
        f"""
        <style>
        @import url(
          'https://fonts.googleapis.com/css2?family=Yeseva+One&display=swap'
        );

        .stApp {{
            {background_css}
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #713247;
        }}

        html, body, [class*="st-"],
        button, input, label, p, h1, h2, h3,
        span, div, textarea {{
            font-family: 'Yeseva One', Georgia, serif !important;
        }}

        [data-testid="stHeader"] {{
            background: rgba(255, 255, 255, 0.12);
        }}

        .block-container {{
            padding-top: 1.5rem;
            max-width: 1200px;
        }}

        h1, h2, h3, p, label,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"] {{
            color: #713247;
        }}

        h1 {{
            font-size: clamp(32px, 4vw, 48px) !important;
        }}

        h2 {{
            font-size: 30px !important;
        }}

        p, label, .stCaption {{
            font-size: 17px;
            line-height: 1.55;
        }}

        .subtitle {{
            color: #713247;
            font-size: 19px;
            text-align: center;
            font-weight: bold;
        }}

        .sakura-card {{
            background: rgba(255, 250, 251, 0.96);
            border: 2px solid #d990a6;
            border-radius: 22px;
            padding: 20px;
            box-shadow: 0 8px 24px #8d385020;
        }}

        div.stButton > button {{
            color: #702b45 !important;
            background: #f8dce5 !important;
            border: 2px solid #cf8099 !important;
            border-radius: 18px !important;
            min-height: 48px;
            font-size: 17px !important;
            font-weight: bold !important;
            box-shadow: 0 4px 12px #8d385020;
        }}

        div.stButton > button:hover {{
            background: #edb8ca !important;
            border-color: #a84e6a !important;
            color: #64223b !important;
        }}

        div.stButton > button:disabled {{
            background: #e9e0e3 !important;
            color: #75666b !important;
            border-color: #c8b8be !important;
        }}

        div[data-baseweb="select"] > div {{
            background: #fff8fa;
            border-color: #c97994;
            color: #702b45;
        }}

        [data-testid="stAlert"] {{
            background: rgba(255, 249, 251, 0.97);
            border: 1px solid #d990a6;
        }}

        [data-testid="stMetricValue"] {{
            color: #8f3655 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# TRẠNG THÁI TRÒ CHƠI
# =========================

def go(page):
    st.session_state.page = page
    st.rerun()


if "page" not in st.session_state:
    st.session_state.page = "menu"

if "level" not in st.session_state:
    st.session_state.level = 0

if "unlocked" not in st.session_state:
    st.session_state.unlocked = 0

if "completed" not in st.session_state:
    st.session_state.completed = []

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "board" not in st.session_state:
    st.session_state.board = None

if "puzzle" not in st.session_state:
    st.session_state.puzzle = None

if "hint_count" not in st.session_state:
    st.session_state.hint_count = 0


# =========================
# HIỆU ỨNG CÁNH HOA RƠI
# =========================

PETALS_HTML = """
<style>
.petal {
    position: fixed;
    top: -60px;
    z-index: 999;
    pointer-events: none;
    user-select: none;
    opacity: 0.85;
    animation-name: petal-fall;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
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
    menu_path = ASSETS / "menu.png"
    menu_uri = data_uri(menu_path)

    menu_background = ""
    if menu_uri:
        menu_background = f"""
        background-image:
            linear-gradient(
                rgba(255, 247, 249, 0.10),
                rgba(255, 247, 249, 0.10)
            ),
            url("{menu_uri}");
        """

    st.markdown(
        f"""
        <style>
        @import url(
          'https://fonts.googleapis.com/css2?family=Yeseva+One&display=swap'
        );

        html, body, [class*="st-"], button,
        p, h1, h2, h3, span, div {{
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
            padding-top: 2rem;
            max-width: 1100px;
        }}

        .menu-title {{
            text-align: center;
            font-size: clamp(42px, 6vw, 76px);
            line-height: 1.25;
            font-weight: bold;
            color: #87334f;
            text-shadow:
                0 2px 0 #fff7f9,
                0 5px 18px rgba(120, 43, 70, 0.24);
            margin: 0 auto;
        }}

        /* Nút PLAY NOW ở chính giữa */
        div.stButton > button {{
            color: #702b45 !important;
            background: linear-gradient(
                145deg, #fff0f5, #f0b9ce
            ) !important;
            border: 3px solid #d88ca8 !important;
            border-radius: 50% !important;
            min-height: 150px;
            width: 150px;
            white-space: pre-line !important;
            font-size: 20px !important;
            font-weight: bold !important;
            box-shadow:
                0 0 0 7px rgba(255, 239, 245, 0.65),
                0 8px 24px rgba(117, 39, 69, 0.24);
            transition: transform 0.2s ease;
        }}

        div.stButton > button:hover {{
            background: linear-gradient(
                145deg, #ffe1ec, #e99bb8
            ) !important;
            transform: scale(1.05);
        }}

        .petal {{
            position: fixed;
            top: -60px;
            z-index: 999;
            pointer-events: none;
            user-select: none;
            opacity: 0.85;
            animation: petal-fall linear infinite;
        }}

        @keyframes petal-fall {{
            0% {{ transform: translateY(-5vh) rotate(0deg); }}
            100% {{ transform: translateY(115vh) rotate(600deg); }}
        }}
        </style>

        <h1 class="menu-title">game của thucute</h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(PETALS_HTML, unsafe_allow_html=True)

    # Khoảng cách để nút nằm ở vùng giữa màn hình
    st.markdown("<div style='height:18vh'></div>", unsafe_allow_html=True)

    left, center, right = st.columns([1, 1, 1])

    with center:
        if st.button(
            "🌸\nPLAY NOW\n🌸",
            key="start_game",
            use_container_width=True,
        ):
            components.html(sound_html("click"), height=0)
            go("levels")

    st.markdown("<div style='height:12vh'></div>", unsafe_allow_html=True)


# =========================
# CHỌN MÀN CHƠI
# =========================

elif st.session_state.page == "levels":
    inject_background(ASSETS / "game_bg.png")

    st.markdown(
        "<h1 style='text-align:center'>🌸 Chọn màn chơi 🌸</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='subtitle'>Mỗi màn là một khu vườn mới</p>",
        unsafe_allow_html=True,
    )

    cols = st.columns(5)

    for i, col in enumerate(cols):
        with col:
            unlocked = i <= st.session_state.unlocked
            done = i in st.session_state.completed

            st.markdown(
                "<div class='sakura-card' "
                "style='text-align:center;min-height:150px'>",
                unsafe_allow_html=True,
            )

            if done:
                st.markdown("### 🌸")
            elif unlocked:
                st.markdown("### 🔓")
            else:
                st.markdown("### 🔒")

            st.markdown(f"**{LEVELS[i][0]}**")

            difficulty = [
                "Rất dễ", "Dễ", "Trung bình", "Khó", "Rất khó"
            ][i]
            st.caption(difficulty)

            if done:
                st.success("Hoàn thành")
            elif not unlocked:
                st.caption("Chưa mở khóa")

            if st.button(
                "Chơi" if unlocked else "Đã khóa",
                key=f"level_{i}",
                disabled=not unlocked,
                use_container_width=True,
            ):
                st.session_state.level = i
                st.session_state.puzzle = make_puzzle(i)
                st.session_state.board = [
                    row[:] for row in st.session_state.puzzle
                ]
                st.session_state.status = "playing"
                st.session_state.hint_count = 0
                go("game")

            st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    if st.button("← Về menu"):
        go("menu")


# =========================
# MÀN CHƠI SUDOKU
# =========================

elif st.session_state.page == "game":
    inject_background(ASSETS / "game_bg.png")

    level = st.session_state.level

    st.markdown(
        f"<h1 style='text-align:center'>🌸 {LEVELS[level][0]} 🌸</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='subtitle'>Điền đúng từng con số để khu vườn nở hoa.</p>",
        unsafe_allow_html=True,
    )

    if st.session_state.status == "playing":
        st.info(
            "💡 Mẹo: mỗi hàng, cột và khối 3×3 phải có đủ số từ 1 đến 9."
        )

    puzzle = st.session_state.puzzle
    board = st.session_state.board

    # Hiển thị bảng Sudoku theo chín khối 3×3
    for br in range(3):
        block_cols = st.columns(3, gap="medium")

        for bc in range(3):
            with block_cols[bc]:
                st.markdown(
                    "<div style='background:rgba(255,250,251,.96);"
                    "border:2px solid #c87591;border-radius:9px;"
                    "padding:5px;margin-bottom:8px'>",
                    unsafe_allow_html=True,
                )

                for r in range(br * 3, br * 3 + 3):
                    cells = st.columns(3, gap="small")

                    for c in range(bc * 3, bc * 3 + 3):
                        with cells[c % 3]:
                            fixed = puzzle[r][c] != 0

                            if fixed:
                                st.markdown(
                                    f"""
                                    <div style="
                                        height:39px;
                                        display:flex;
                                        align-items:center;
                                        justify-content:center;
                                        background:#f8dfe7;
                                        border:1px solid #dba3b5;
                                        border-radius:5px;
                                        font-weight:bold;
                                        font-size:19px;
                                        color:#702b45;">
                                        {puzzle[r][c]}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                            else:
                                options = ["—"] + [
                                    str(n) for n in range(1, 10)
                                ]
                                current = (
                                    str(board[r][c])
                                    if board[r][c]
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

                                new_val = (
                                    0 if selected == "—" else int(selected)
                                )

                                if new_val != board[r][c]:
                                    board[r][c] = new_val

                                    if new_val:
                                        if new_val != SOLUTION[r][c]:
                                            st.session_state.status = "lost"
                                        elif all(
                                            board[rr][cc] == SOLUTION[rr][cc]
                                            for rr in range(9)
                                            for cc in range(9)
                                        ):
                                            st.session_state.status = "won"

                                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # KẾT QUẢ THẮNG / THUA
    # =========================

    if st.session_state.status == "lost":
        components.html(sound_html("lose"), height=0)

        st.error("🍂 Rất tiếc! Bạn đã điền sai số. Màn chơi kết thúc.")

        left, right = st.columns(2)

        with left:
            if st.button("🔄 Chơi lại", use_container_width=True):
                st.session_state.puzzle = make_puzzle(level)
                st.session_state.board = [
                    row[:] for row in st.session_state.puzzle
                ]
                st.session_state.status = "playing"
                st.session_state.hint_count = 0
                go("game")

        with right:
            if st.button("🌸 Chọn màn khác", use_container_width=True):
                go("levels")

    elif st.session_state.status == "won":
        components.html(sound_html("win"), height=0)

        st.success("🌸 Tuyệt vời! Bạn đã hoàn thành màn chơi!")

        if level not in st.session_state.completed:
            st.session_state.completed.append(level)

        st.session_state.unlocked = max(
            st.session_state.unlocked,
            min(4, level + 1),
        )

        if level < 4:
            if st.button("➡️ Sang màn tiếp theo", use_container_width=True):
                st.session_state.level = level + 1
                st.session_state.puzzle = make_puzzle(level + 1)
                st.session_state.board = [
                    row[:] for row in st.session_state.puzzle
                ]
                st.session_state.status = "playing"
                st.session_state.hint_count = 0
                go("game")
        else:
            st.balloons()
            st.markdown("### 🏆 Bạn đã chinh phục cả 5 khu vườn Sakura!")

        if st.button("Chọn màn chơi"):
            go("levels")

    else:
        left, middle, right = st.columns(3)

        with left:
            if st.button("💡 Gợi ý", use_container_width=True):
                empty = [
                    (r, c)
                    for r in range(9)
                    for c in range(9)
                    if puzzle[r][c] == 0 and board[r][c] == 0
                ]

                if empty:
                    r, c = random.choice(empty)
                    board[r][c] = SOLUTION[r][c]
                    st.session_state.hint_count += 1
                    st.rerun()
                else:
                    st.info("Không còn ô trống để gợi ý.")

        with middle:
            st.metric("Gợi ý đã dùng", st.session_state.hint_count)

        with right:
            if st.button("🏠 Về chọn màn", use_container_width=True):
                go("levels")

    # =========================
    # KIỂM TRA ÂM THANH
    # =========================

    with st.expander("🎵 Âm thanh"):
        st.markdown("**Nhạc nền — nhấn Play để nghe:**")
        components.html(
            sound_html("music", autoplay=False, loop=True),
            height=60,
        )

        st.markdown("**Âm thanh khi bấm:**")
        components.html(sound_html("click", autoplay=False), height=60)

        st.markdown("**Âm thanh chiến thắng:**")
        components.html(sound_html("win", autoplay=False), height=60)

        st.markdown("**Âm thanh thua cuộc:**")
        components.html(sound_html("lose", autoplay=False), height=60)

        st.caption(
            "Một số trình duyệt chặn âm thanh tự phát. "
            "Hãy nhấn Play để kiểm tra nhạc nền."
        )
