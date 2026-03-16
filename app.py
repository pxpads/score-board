import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ScoreBoard",
    page_icon="🏆",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Dark background */
.stApp {
    background-color: #0d0f14;
    color: #e8eaf0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #13161e !important;
    border-right: 1px solid #1e2230;
}

/* Title */
h1 {
    font-family: 'Space Mono', monospace !important;
    color: #ffffff !important;
    letter-spacing: -1px;
}
h2, h3 {
    font-family: 'Space Mono', monospace !important;
    color: #c0c8e0 !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #1a1d28;
    border: 1px solid #252a3a;
    border-radius: 12px;
    padding: 16px;
}
[data-testid="metric-container"] label {
    color: #6b7280 !important;
    font-size: 0.75rem !important;
    letter-spacing: 1px;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #7dd3fc !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 2rem !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.5px;
    transition: opacity 0.2s;
}
.stButton > button:hover {
    opacity: 0.85;
}

/* Number inputs */
.stNumberInput input {
    background: #1a1d28 !important;
    color: #e8eaf0 !important;
    border: 1px solid #252a3a !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
}

/* Text inputs */
.stTextInput input {
    background: #1a1d28 !important;
    color: #e8eaf0 !important;
    border: 1px solid #252a3a !important;
    border-radius: 8px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #252a3a;
    border-radius: 12px;
    overflow: hidden;
}

/* Divider */
hr {
    border-color: #1e2230 !important;
}

/* Success / info */
.stAlert {
    border-radius: 10px !important;
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"] > div {
    background: #1a1d28 !important;
    border-color: #252a3a !important;
    color: #e8eaf0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "players" not in st.session_state:
    st.session_state.players = []
if "scores" not in st.session_state:
    st.session_state.scores = {}   # {player: [score_game1, score_game2, ...]}
if "game_count" not in st.session_state:
    st.session_state.game_count = 0
if "setup_done" not in st.session_state:
    st.session_state.setup_done = False

# ── SIDEBAR – Player Setup ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Setup Pemain")
    st.markdown("---")

    num_players = st.number_input(
        "Jumlah Pemain", min_value=2, max_value=10, value=2, step=1
    )

    st.markdown("**Nama Pemain**")
    names = []
    for i in range(int(num_players)):
        name = st.text_input(
            f"Pemain {i+1}", value=f"Pemain {i+1}", key=f"name_{i}"
        )
        names.append(name.strip() if name.strip() else f"Pemain {i+1}")

    if st.button("✅ Mulai / Reset Game", use_container_width=True):
        st.session_state.players = names
        st.session_state.scores = {p: [] for p in names}
        st.session_state.game_count = 0
        st.session_state.setup_done = True
        st.rerun()

    if st.session_state.setup_done:
        st.markdown("---")
        st.markdown(f"**Game Selesai:** `{st.session_state.game_count}`")
        st.markdown(f"**Pemain Aktif:** `{len(st.session_state.players)}`")

# ── MAIN AREA ────────────────────────────────────────────────────────────────
st.markdown("# 🏆 ScoreBoard")
st.markdown("*Aplikasi pencatat skor multi-pemain*")
st.markdown("---")

if not st.session_state.setup_done:
    st.info("👈  Atur jumlah dan nama pemain di sidebar, lalu klik **Mulai / Reset Game**.")
    st.stop()

players = st.session_state.players
scores  = st.session_state.scores

# ── Input Skor Game Baru ──────────────────────────────────────────────────────
st.markdown(f"### ➕ Input Skor — Game {st.session_state.game_count + 1}")

cols = st.columns(min(len(players), 5))
game_input = {}
for idx, player in enumerate(players):
    with cols[idx % len(cols)]:
        game_input[player] = st.number_input(
            player, value=0, step=1, key=f"input_{player}"
        )

if st.button("💾 Simpan Skor Game Ini", use_container_width=False):
    for player in players:
        scores[player].append(game_input[player])
    st.session_state.game_count += 1
    st.success(f"✔ Skor Game {st.session_state.game_count} berhasil disimpan!")
    st.rerun()

st.markdown("---")

# ── Rekap Skor ────────────────────────────────────────────────────────────────
if st.session_state.game_count == 0:
    st.info("Belum ada data skor. Tambahkan skor game pertama di atas.")
    st.stop()

st.markdown("### 📋 Rekap Skor Per Game")

# Build table
game_labels = [f"Game {i+1}" for i in range(st.session_state.game_count)]
df = pd.DataFrame(scores, index=game_labels)
df.index.name = "Game"

# Add total row
total_row = pd.DataFrame(
    {p: [sum(scores[p])] for p in players},
    index=["**TOTAL**"]
)
df_display = pd.concat([df, total_row])
st.dataframe(df_display, use_container_width=True)

# ── Summary Metrics ───────────────────────────────────────────────────────────
totals = {p: sum(scores[p]) for p in players}
leader = max(totals, key=totals.get)

st.markdown("---")
st.markdown("### 🥇 Ringkasan")

metric_cols = st.columns(len(players))
for idx, player in enumerate(players):
    with metric_cols[idx]:
        delta = "👑 LEADER" if player == leader else None
        st.metric(player, totals[player], delta=delta)

st.markdown("---")

# ── Charts ───────────────────────────────────────────────────────────────────
chart_col1, chart_col2 = st.columns(2)

COLORS = [
    "#7dd3fc", "#818cf8", "#34d399", "#f472b6",
    "#fbbf24", "#f87171", "#a78bfa", "#2dd4bf",
    "#fb923c", "#e879f9"
]

# Bar Chart – Total Skor (sorted descending)
with chart_col1:
    st.markdown("### 📊 Total Skor per Pemain")
    bar_df = pd.DataFrame({"Pemain": list(totals.keys()), "Total Skor": list(totals.values())})
    bar_df = bar_df.sort_values("Total Skor", ascending=False).reset_index(drop=True)
    # Assign colors based on sorted order
    bar_colors = [COLORS[i % len(COLORS)] for i in range(len(bar_df))]
    fig_bar = px.bar(
        bar_df, x="Pemain", y="Total Skor",
        color="Pemain",
        color_discrete_sequence=bar_colors,
        text="Total Skor",
        category_orders={"Pemain": bar_df["Pemain"].tolist()},
    )
    fig_bar.update_traces(textposition="outside", textfont_size=13)
    fig_bar.update_layout(
        paper_bgcolor="#0d0f14",
        plot_bgcolor="#13161e",
        font=dict(family="DM Sans", color="#c0c8e0"),
        showlegend=False,
        xaxis=dict(gridcolor="#1e2230", title=""),
        yaxis=dict(gridcolor="#1e2230", title="Total Skor"),
        margin=dict(t=20, b=10),
        height=380,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Line Chart – Skor Kumulatif per Game
with chart_col2:
    st.markdown("### 📈 Tren Skor Kumulatif")
    fig_line = go.Figure()
    for idx, player in enumerate(players):
        cumulative = []
        running = 0
        for s in scores[player]:
            running += s
            cumulative.append(running)
        fig_line.add_trace(go.Scatter(
            x=game_labels,
            y=cumulative,
            mode="lines+markers",
            name=player,
            line=dict(color=COLORS[idx % len(COLORS)], width=2.5),
            marker=dict(size=8),
        ))
    fig_line.update_layout(
        paper_bgcolor="#0d0f14",
        plot_bgcolor="#13161e",
        font=dict(family="DM Sans", color="#c0c8e0"),
        legend=dict(bgcolor="#13161e", bordercolor="#1e2230", borderwidth=1),
        xaxis=dict(gridcolor="#1e2230", title="Game"),
        yaxis=dict(gridcolor="#1e2230", title="Total Skor Kumulatif"),
        margin=dict(t=20, b=10),
        height=380,
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ── Line Chart – Skor Per Game (non-kumulatif) ────────────────────────────────
st.markdown("### 📉 Skor per Game")
fig_raw = go.Figure()
for idx, player in enumerate(players):
    fig_raw.add_trace(go.Scatter(
        x=game_labels,
        y=scores[player],
        mode="lines+markers",
        name=player,
        line=dict(color=COLORS[idx % len(COLORS)], width=2, dash="dot"),
        marker=dict(size=7, symbol="diamond"),
    ))
fig_raw.update_layout(
    paper_bgcolor="#0d0f14",
    plot_bgcolor="#13161e",
    font=dict(family="DM Sans", color="#c0c8e0"),
    legend=dict(bgcolor="#13161e", bordercolor="#1e2230", borderwidth=1),
    xaxis=dict(gridcolor="#1e2230", title="Game"),
    yaxis=dict(gridcolor="#1e2230", title="Skor per Game"),
    margin=dict(t=20, b=10),
    height=340,
)
st.plotly_chart(fig_raw, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("ScoreBoard · Built with Streamlit + Plotly")
