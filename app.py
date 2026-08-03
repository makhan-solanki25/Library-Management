"""
=====================================================================================
 PREMIUM LIBRARY MANAGEMENT SYSTEM
=====================================================================================
 A single-file, professional Streamlit application demonstrating:
   - Object-Oriented Programming (Inheritance & Polymorphism)
   - SQLite persistence (auto-created on first run)
   - A modern, dark, glassmorphism-style SaaS dashboard UI
   - Full CRUD (Create, Read, Update, Delete)
   - Search / Filter
   - Plotly Analytics
   - CSV / Excel export

 Run with:
     pip install streamlit plotly pandas
     streamlit run app.py

 Author: Makhan Solanki
=====================================================================================
"""

import io
import sqlite3
from datetime import datetime, date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =====================================================================================
# 1. PAGE CONFIGURATION  (must be the first Streamlit call)
# =====================================================================================
st.set_page_config(
    page_title="Library Management System | Premium",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_NAME = "library.db"


# =====================================================================================
# 2. OBJECT-ORIENTED MODEL LAYER  (Inheritance + Polymorphism)
# =====================================================================================
class LibraryItem:
    """Base class for every item that can live inside the library."""

    icon = "📦"
    type_name = "Item"

    def __init__(self, title: str, author: str = "", issue_number=None, publish_date=None):
        self.title = title
        self.author = author
        self.issue_number = issue_number
        self.publish_date = publish_date

    def display_info(self) -> dict:
        """Base representation. Overridden (polymorphism) by every subclass."""
        return {
            "type": self.type_name,
            "title": self.title,
            "author": self.author,
            "issue_number": self.issue_number,
            "publish_date": self.publish_date,
        }

    def summary_line(self) -> str:
        """A short human readable summary. Polymorphic across subclasses."""
        return f"{self.icon} {self.type_name}: {self.title}"


class Book(LibraryItem):
    """A physical or digital book, identified by title & author."""

    icon = "📖"
    type_name = "Book"

    def __init__(self, title: str, author: str):
        super().__init__(title=title, author=author)

    def display_info(self) -> dict:
        info = super().display_info()
        info["subtitle"] = f"by {self.author}" if self.author else ""
        return info

    def summary_line(self) -> str:
        return f"{self.icon} '{self.title}' written by {self.author}"


class Magazine(LibraryItem):
    """A periodical publication identified by name & issue number."""

    icon = "📰"
    type_name = "Magazine"

    def __init__(self, name: str, issue_number: int):
        super().__init__(title=name, issue_number=issue_number)

    def display_info(self) -> dict:
        info = super().display_info()
        info["subtitle"] = f"Issue #{self.issue_number}"
        return info

    def summary_line(self) -> str:
        return f"{self.icon} '{self.title}' - Issue #{self.issue_number}"


class Newspaper(LibraryItem):
    """A daily/periodic newspaper identified by name & publish date."""

    icon = "🗞"
    type_name = "Newspaper"

    def __init__(self, name: str, publish_date: str):
        super().__init__(title=name, publish_date=publish_date)

    def display_info(self) -> dict:
        info = super().display_info()
        info["subtitle"] = f"Published {self.publish_date}"
        return info

    def summary_line(self) -> str:
        return f"{self.icon} '{self.title}' dated {self.publish_date}"


# =====================================================================================
# 3. DATABASE LAYER  (SQLite - auto created on first run)
# =====================================================================================
def get_connection():
    """Return a new SQLite connection to library.db."""
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    """Create the `library` table automatically if it does not already exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            issue_number INTEGER,
            publish_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def add_item_to_db(item: LibraryItem):
    """Persist a LibraryItem (Book / Magazine / Newspaper) into SQLite."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO library (type, title, author, issue_number, publish_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            item.type_name,
            item.title,
            item.author,
            item.issue_number,
            item.publish_date,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


def update_item_in_db(item_id, title, author, issue_number, publish_date):
    """Update an existing row identified by id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE library
        SET title = ?, author = ?, issue_number = ?, publish_date = ?
        WHERE id = ?
        """,
        (title, author, issue_number, publish_date, item_id),
    )
    conn.commit()
    conn.close()


def delete_item_from_db(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM library WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


def fetch_all_items() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM library ORDER BY id DESC", conn)
    conn.close()
    return df


def fetch_counts():
    df = fetch_all_items()
    total = len(df)
    books = int((df["type"] == "Book").sum()) if total else 0
    mags = int((df["type"] == "Magazine").sum()) if total else 0
    news = int((df["type"] == "Newspaper").sum()) if total else 0
    return total, books, mags, news


# Initialize the database as soon as the app starts
init_db()


# =====================================================================================
# 4. CUSTOM CSS  (dark theme, glassmorphism, gradients, hover animations)
# =====================================================================================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* ---------- App background ---------- */
    .stApp {
        background: radial-gradient(circle at 10% 0%, #1a2035 0%, #0b0e17 45%, #05070c 100%);
        color: #e5e7eb;
    }

    /* Hide default Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10131f 0%, #0a0d16 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem;
    }

    /* ---------- Hero banner ---------- */
    .hero {
        background: linear-gradient(120deg, #6d28d9 0%, #2563eb 55%, #0891b2 100%);
        background-size: 200% 200%;
        animation: gradientShift 10s ease infinite;
        padding: 40px 44px;
        border-radius: 22px;
        box-shadow: 0 20px 60px -20px rgba(37, 99, 235, 0.55);
        position: relative;
        overflow: hidden;
        margin-bottom: 26px;
    }
    .hero::after {
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 85% 20%, rgba(255,255,255,0.18), transparent 45%);
    }
    @keyframes gradientShift {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .hero h1 {
        font-family: 'Poppins', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero p {
        color: rgba(255,255,255,0.88);
        font-size: 1.05rem;
        margin-top: 8px;
        font-weight: 500;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.16);
        backdrop-filter: blur(6px);
        border: 1px solid rgba(255,255,255,0.25);
        color: #fff;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 14px;
        letter-spacing: 0.3px;
    }

    /* ---------- Glass cards ---------- */
    .glass-card {
        background: rgba(255,255,255,0.045);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 18px;
        padding: 22px 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        margin-bottom: 18px;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99,102,241,0.55);
        box-shadow: 0 16px 40px rgba(79,70,229,0.28);
    }

    /* ---------- Item cards (library view) ---------- */
    .item-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.055), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 5px solid #6366f1;
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 16px;
        transition: all 0.25s ease;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }
    .item-card:hover {
        transform: translateY(-3px) scale(1.005);
        box-shadow: 0 14px 34px rgba(99,102,241,0.25);
        border-left-color: #22d3ee;
    }
    .item-card .item-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 2px;
    }
    .item-card .item-sub {
        color: #94a3b8;
        font-size: 0.88rem;
        margin-bottom: 10px;
    }
    .type-pill {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }
    .pill-book { background: rgba(34,197,94,0.16); color: #4ade80; border: 1px solid rgba(34,197,94,0.35);}
    .pill-magazine { background: rgba(59,130,246,0.16); color: #60a5fa; border: 1px solid rgba(59,130,246,0.35);}
    .pill-newspaper { background: rgba(244,114,182,0.16); color: #f472b6; border: 1px solid rgba(244,114,182,0.35);}

    /* ---------- Metric cards ---------- */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 16px 18px 10px 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(99,102,241,0.5);
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc;
        font-weight: 800;
    }

    /* ---------- Buttons ---------- */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1, #2563eb);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.55rem 1.1rem;
        font-weight: 600;
        letter-spacing: 0.2px;
        transition: all 0.2s ease;
        box-shadow: 0 6px 18px rgba(79,70,229,0.35);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 26px rgba(79,70,229,0.5);
        filter: brightness(1.08);
    }

    /* Danger buttons (delete) get styled via key prefix using nth-of-type is tricky in Streamlit,
       so we rely on emoji + confirm flow instead for clarity. */

    /* ---------- Inputs ---------- */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: #f1f5f9 !important;
    }
    .stSelectbox>div>div {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255,255,255,0.03);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.07);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 600;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #2563eb);
        color: white !important;
    }

    /* ---------- Section headers ---------- */
    .section-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 4px;
    }
    .section-sub {
        color: #94a3b8;
        font-size: 0.92rem;
        margin-bottom: 18px;
    }

    /* ---------- Empty state ---------- */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        border: 2px dashed rgba(255,255,255,0.12);
        border-radius: 20px;
        background: rgba(255,255,255,0.02);
    }
    .empty-state .emoji { font-size: 3.2rem; margin-bottom: 10px; }
    .empty-state h3 { color: #e2e8f0; margin-bottom: 4px; }
    .empty-state p { color: #94a3b8; }

    /* ---------- Footer ---------- */
    .app-footer {
        margin-top: 40px;
        padding: 18px 24px;
        border-radius: 16px;
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        text-align: center;
        color: #94a3b8;
        font-size: 0.85rem;
    }
    .app-footer b { color: #e2e8f0; }

    /* Sidebar logo */
    .side-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 4px 18px 4px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 16px;
    }
    .side-logo .logo-icon {
        font-size: 1.8rem;
    }
    .side-logo .logo-text {
        font-family: 'Poppins', sans-serif;
        font-weight: 800;
        font-size: 1.15rem;
        color: #f8fafc;
        line-height: 1.1;
    }
    .side-logo .logo-sub {
        font-size: 0.7rem;
        color: #818cf8;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# =====================================================================================
# 5. SESSION STATE
# =====================================================================================
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None
if "edit_item_id" not in st.session_state:
    st.session_state.edit_item_id = None
if "nav" not in st.session_state:
    st.session_state.nav = "Dashboard"


# =====================================================================================
# 6. SIDEBAR NAVIGATION
# =====================================================================================
with st.sidebar:
    st.markdown(
        """
        <div class="side-logo">
            <div class="logo-icon">📚</div>
            <div>
                <div class="logo-text">LibraryPro</div>
                <div class="logo-sub">PREMIUM EDITION</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav = st.radio(
        "Navigation",
        ["🏠 Dashboard", "➕ Add Item", "📚 Library", "🔍 Search", "📊 Analytics", "ℹ️ About"],
        label_visibility="collapsed",
    )
    st.session_state.nav = nav.split(" ", 1)[1]

    st.markdown("---")
    total, books, mags, news = fetch_counts()
    st.caption("QUICK STATS")
    st.markdown(f"📖 **{books}** Books")
    st.markdown(f"📰 **{mags}** Magazines")
    st.markdown(f"🗞 **{news}** Newspapers")
    st.markdown("---")
    st.caption(f"🟢 Database: `{DB_NAME}` connected")
    st.caption(f"📅 {date.today().strftime('%B %d, %Y')}")


page = st.session_state.nav


# =====================================================================================
# 7. SHARED HERO HEADER
# =====================================================================================
def render_hero(title, subtitle, badge="LIBRARY MANAGEMENT SYSTEM"):
    st.markdown(
        f"""
        <div class="hero">
            <span class="hero-badge">{badge}</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def type_pill(item_type):
    css_class = {"Book": "pill-book", "Magazine": "pill-magazine", "Newspaper": "pill-newspaper"}.get(
        item_type, "pill-book"
    )
    return f'<span class="type-pill {css_class}">{item_type}</span>'


def item_icon(item_type):
    return {"Book": "📖", "Magazine": "📰", "Newspaper": "🗞"}.get(item_type, "📦")


# =====================================================================================
# 8. PAGE: DASHBOARD
# =====================================================================================
if page == "Dashboard":
    render_hero(
        "Welcome back, Librarian 👋",
        "Here's a real-time snapshot of your entire library collection.",
    )

    total, books, mags, news = fetch_counts()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Total Items", total)
    c2.metric("📖 Books", books)
    c3.metric("📰 Magazines", mags)
    c4.metric("🗞 Newspapers", news)

    st.write("")
    left, right = st.columns([1.3, 1])

    with left:
        st.markdown('<div class="section-title">Collection Breakdown</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Distribution of items by type</div>', unsafe_allow_html=True)
        df = fetch_all_items()
        if not df.empty:
            counts_df = df["type"].value_counts().reset_index()
            counts_df.columns = ["Type", "Count"]
            fig = px.pie(
                counts_df,
                names="Type",
                values="Count",
                hole=0.55,
                color="Type",
                color_discrete_map={"Book": "#4ade80", "Magazine": "#60a5fa", "Newspaper": "#f472b6"},
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e5e7eb",
                legend=dict(orientation="h", y=-0.1),
                margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="emoji">📭</div>
                    <h3>No data yet</h3>
                    <p>Add your first item to see the breakdown chart.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown('<div class="section-title">Recent Activity</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Last 5 items added</div>', unsafe_allow_html=True)
        df = fetch_all_items()
        if not df.empty:
            for _, row in df.head(5).iterrows():
                st.markdown(
                    f"""
                    <div class="glass-card" style="padding:14px 18px; margin-bottom:10px;">
                        <b>{item_icon(row['type'])} {row['title']}</b><br>
                        {type_pill(row['type'])} <span style="color:#94a3b8;font-size:0.8rem;"> · added {row['created_at']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Nothing here yet — start by adding a book, magazine, or newspaper!")

# =====================================================================================
# 9. PAGE: ADD ITEM
# =====================================================================================
elif page == "Add Item":
    render_hero("Add a New Item ➕", "Grow your collection — pick a type and fill in the details.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    option = st.selectbox("📂 Select Item Type", ["Book", "Magazine", "Newspaper"])

    if option == "Book":
        col1, col2 = st.columns(2)
        title = col1.text_input("📖 Book Title", placeholder="e.g. Atomic Habits")
        author = col2.text_input("✍️ Author", placeholder="e.g. James Clear")

        if st.button("✅ Add Book", use_container_width=True):
            if title.strip() and author.strip():
                with st.spinner("Saving book to the library..."):
                    add_item_to_db(Book(title.strip(), author.strip()))
                st.success(f"🎉 Book '{title}' added successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("⚠️ Please fill in both the title and the author.")

    elif option == "Magazine":
        col1, col2 = st.columns(2)
        name = col1.text_input("📰 Magazine Name", placeholder="e.g. National Geographic")
        issue = col2.number_input("🔢 Issue Number", min_value=1, max_value=99999, value=1)

        if st.button("✅ Add Magazine", use_container_width=True):
            if name.strip():
                with st.spinner("Saving magazine to the library..."):
                    add_item_to_db(Magazine(name.strip(), int(issue)))
                st.success(f"🎉 Magazine '{name}' (Issue #{issue}) added successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("⚠️ Please enter the magazine name.")

    else:  # Newspaper
        col1, col2 = st.columns(2)
        name = col1.text_input("🗞 Newspaper Name", placeholder="e.g. The Daily Times")
        d = col2.date_input("📅 Publish Date", date.today())

        if st.button("✅ Add Newspaper", use_container_width=True):
            if name.strip():
                with st.spinner("Saving newspaper to the library..."):
                    add_item_to_db(Newspaper(name.strip(), d.strftime("%d-%m-%Y")))
                st.success(f"🎉 Newspaper '{name}' added successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("⚠️ Please enter the newspaper name.")

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================================
# 10. PAGE: LIBRARY  (view / edit / delete)
# =====================================================================================
elif page == "Library":
    render_hero("Your Library 📚", "Browse, edit, and manage every item in your collection.")

    df = fetch_all_items()

    filter_col, export_col1, export_col2 = st.columns([2, 1, 1])
    with filter_col:
        type_filter = st.selectbox("Filter by type", ["All", "Book", "Magazine", "Newspaper"])

    if type_filter != "All":
        df = df[df["type"] == type_filter]

    with export_col1:
        csv_bytes = fetch_all_items().to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Export CSV", data=csv_bytes, file_name="library_export.csv", mime="text/csv", use_container_width=True
        )
    with export_col2:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            fetch_all_items().to_excel(writer, index=False, sheet_name="Library")
        st.download_button(
            "⬇️ Export Excel",
            data=excel_buffer.getvalue(),
            file_name="library_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.write("")

    if df.empty:
        st.markdown(
            """
            <div class="empty-state">
                <div class="emoji">📭</div>
                <h3>Your library is empty</h3>
                <p>Head over to <b>Add Item</b> to add your first book, magazine, or newspaper.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for _, row in df.iterrows():
            item_id = int(row["id"])
            is_editing = st.session_state.edit_item_id == item_id
            is_confirming = st.session_state.confirm_delete_id == item_id

            detail = ""
            if row["type"] == "Book":
                detail = f"by {row['author']}" if row["author"] else "Author unknown"
            elif row["type"] == "Magazine":
                detail = f"Issue #{int(row['issue_number'])}" if pd.notna(row["issue_number"]) else ""
            else:
                detail = f"Published {row['publish_date']}" if row["publish_date"] else ""

            st.markdown(
                f"""
                <div class="item-card">
                    <div class="item-title">{item_icon(row['type'])} {row['title']}</div>
                    <div class="item-sub">{detail} &nbsp;•&nbsp; Added {row['created_at']}</div>
                    {type_pill(row['type'])}
                </div>
                """,
                unsafe_allow_html=True,
            )

            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 4])
            if btn_col1.button("✏️ Edit", key=f"edit_{item_id}", use_container_width=True):
                st.session_state.edit_item_id = None if is_editing else item_id
                st.session_state.confirm_delete_id = None
                st.rerun()
            if btn_col2.button("🗑️ Delete", key=f"del_{item_id}", use_container_width=True):
                st.session_state.confirm_delete_id = item_id
                st.session_state.edit_item_id = None
                st.rerun()

            if is_confirming:
                st.warning(f"⚠️ Are you sure you want to permanently delete **{row['title']}**?")
                yes_col, no_col = st.columns(2)
                if yes_col.button("✅ Yes, delete it", key=f"yes_{item_id}", use_container_width=True):
                    delete_item_from_db(item_id)
                    st.session_state.confirm_delete_id = None
                    st.success("Item deleted.")
                    st.rerun()
                if no_col.button("❌ Cancel", key=f"no_{item_id}", use_container_width=True):
                    st.session_state.confirm_delete_id = None
                    st.rerun()

            if is_editing:
                with st.form(key=f"edit_form_{item_id}"):
                    st.markdown(f"**Editing: {row['type']}**")
                    new_title = st.text_input("Title", value=row["title"])
                    new_author = st.text_input("Author", value=row["author"] or "")
                    new_issue = st.number_input(
                        "Issue Number", min_value=0, max_value=99999,
                        value=int(row["issue_number"]) if pd.notna(row["issue_number"]) else 0,
                    )
                    new_date = st.text_input("Publish Date", value=row["publish_date"] or "")
                    save_col, cancel_col = st.columns(2)
                    save = save_col.form_submit_button("💾 Save Changes", use_container_width=True)
                    cancel = cancel_col.form_submit_button("✖️ Cancel", use_container_width=True)

                    if save:
                        update_item_in_db(
                            item_id,
                            new_title.strip(),
                            new_author.strip(),
                            new_issue if new_issue else None,
                            new_date.strip() if new_date.strip() else None,
                        )
                        st.session_state.edit_item_id = None
                        st.success("Item updated successfully!")
                        st.rerun()
                    if cancel:
                        st.session_state.edit_item_id = None
                        st.rerun()

# =====================================================================================
# 11. PAGE: SEARCH
# =====================================================================================
elif page == "Search":
    render_hero("Search the Library 🔍", "Find items instantly by title, author, or type.")

    df = fetch_all_items()

    s_col1, s_col2 = st.columns([2, 1])
    query = s_col1.text_input("🔎 Search by title or author", placeholder="Start typing...")
    type_choice = s_col2.selectbox("Filter by type", ["All", "Book", "Magazine", "Newspaper"])

    if type_choice != "All":
        df = df[df["type"] == type_choice]

    if query.strip():
        q = query.lower().strip()
        mask = df["title"].str.lower().str.contains(q, na=False) | df["author"].str.lower().str.contains(q, na=False)
        results = df[mask]
    else:
        results = df if type_choice != "All" else pd.DataFrame()

    if query.strip() or type_choice != "All":
        st.markdown(f'<div class="section-sub">Found {len(results)} matching item(s)</div>', unsafe_allow_html=True)
        if results.empty:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="emoji">🔍</div>
                    <h3>No matching items found</h3>
                    <p>Try a different keyword or filter.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for _, row in results.iterrows():
                detail = ""
                if row["type"] == "Book":
                    detail = f"by {row['author']}" if row["author"] else "Author unknown"
                elif row["type"] == "Magazine":
                    detail = f"Issue #{int(row['issue_number'])}" if pd.notna(row["issue_number"]) else ""
                else:
                    detail = f"Published {row['publish_date']}" if row["publish_date"] else ""
                st.markdown(
                    f"""
                    <div class="item-card">
                        <div class="item-title">{item_icon(row['type'])} {row['title']}</div>
                        <div class="item-sub">{detail}</div>
                        {type_pill(row['type'])}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("Start typing above, or pick a type filter, to search your library.")

# =====================================================================================
# 12. PAGE: ANALYTICS
# =====================================================================================
elif page == "Analytics":
    render_hero("Analytics 📊", "Visual insights into your library's growth and composition.")

    df = fetch_all_items()
    total, books, mags, news = fetch_counts()

    if df.empty:
        st.markdown(
            """
            <div class="empty-state">
                <div class="emoji">📈</div>
                <h3>No analytics available yet</h3>
                <p>Add a few items to unlock charts and insights.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📦 Total Items", total)
        m2.metric("📖 Books", books, f"{(books/total*100):.0f}%")
        m3.metric("📰 Magazines", mags, f"{(mags/total*100):.0f}%")
        m4.metric("🗞 Newspapers", news, f"{(news/total*100):.0f}%")

        st.write("")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown('<div class="section-title">Type Distribution</div>', unsafe_allow_html=True)
            counts_df = df["type"].value_counts().reset_index()
            counts_df.columns = ["Type", "Count"]
            fig_pie = px.pie(
                counts_df, names="Type", values="Count", hole=0.5,
                color="Type",
                color_discrete_map={"Book": "#4ade80", "Magazine": "#60a5fa", "Newspaper": "#f472b6"},
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e5e7eb", margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with chart_col2:
            st.markdown('<div class="section-title">Items by Type</div>', unsafe_allow_html=True)
            fig_bar = px.bar(
                counts_df, x="Type", y="Count", color="Type", text="Count",
                color_discrete_map={"Book": "#4ade80", "Magazine": "#60a5fa", "Newspaper": "#f472b6"},
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e5e7eb", showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown('<div class="section-title">Growth Over Time</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Cumulative items added per day</div>', unsafe_allow_html=True)
        growth_df = df.copy()
        growth_df["created_at"] = pd.to_datetime(growth_df["created_at"])
        growth_df["day"] = growth_df["created_at"].dt.date
        daily = growth_df.groupby("day").size().reset_index(name="added")
        daily = daily.sort_values("day")
        daily["cumulative"] = daily["added"].cumsum()

        fig_line = go.Figure()
        fig_line.add_trace(
            go.Scatter(
                x=daily["day"], y=daily["cumulative"], mode="lines+markers",
                line=dict(color="#818cf8", width=3),
                marker=dict(size=8, color="#22d3ee"),
                fill="tozeroy", fillcolor="rgba(129,140,248,0.15)",
            )
        )
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e5e7eb", margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title="Date", yaxis_title="Total Items",
        )
        st.plotly_chart(fig_line, use_container_width=True)

# =====================================================================================
# 13. PAGE: ABOUT
# =====================================================================================
elif page == "About":
    render_hero("About This Project ℹ️", "A showcase of clean OOP design and modern Streamlit UI.")

    st.markdown(
        """
        <div class="glass-card">
        <h3>✨ Features</h3>
        <ul>
            <li>Object-Oriented Programming — Inheritance & Polymorphism</li>
            <li>SQLite database, auto-created on first run</li>
            <li>Full CRUD: Add, View, Edit, Delete (with confirmation)</li>
            <li>Live search & type filtering</li>
            <li>Plotly-powered analytics (pie, bar, line charts)</li>
            <li>CSV / Excel export</li>
            <li>Premium dark, glassmorphism UI with smooth animations</li>
        </ul>

        <h3>🏗️ Architecture</h3>
        <p><code>LibraryItem</code> is the abstract-style base class. <code>Book</code>,
        <code>Magazine</code>, and <code>Newspaper</code> each inherit from it and override
        <code>display_info()</code> and <code>summary_line()</code> — a direct demonstration
        of polymorphism, since the same method name behaves differently per subclass.</p>

        <h3>🛠️ Tech Stack</h3>
        <p>Python · Streamlit · SQLite3 · Pandas · Plotly</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =====================================================================================
# 14. FOOTER  (shown on every page)
# =====================================================================================
total, books, mags, news = fetch_counts()
st.markdown(
    f"""
    <div class="app-footer">
        Made with ❤️ by <b>Makhan Solanki</b> &nbsp;|&nbsp;
        📅 {date.today().strftime('%B %d, %Y')} &nbsp;|&nbsp;
        🟢 Database Status: <b>Connected</b> ({DB_NAME}) &nbsp;|&nbsp;
        📦 Total Records: <b>{total}</b>
    </div>
    """,
    unsafe_allow_html=True,
)