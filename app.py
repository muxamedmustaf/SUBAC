import streamlit as st
import sqlite3
import os
import json
from datetime import datetime

# ==================================================
# 1) إعداد الصفحة
# ==================================================
st.set_page_config(
    page_title="إدارة الحلقة القرآنية",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# 2) التنسيقات (CSS احترافي)
# ==================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
    /* إخفاء عناصر Streamlit الافتراضية */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }

    /* الخط العام */
    html, body, [class*="css"], .stApp {
        font-family: 'Tajawal', -apple-system, sans-serif !important;
        direction: rtl;
    }
    .stApp { background: #f4f7f5; }

    /* نصوص من اليمين */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, div {
        direction: rtl;
        text-align: right;
    }

    /* ====== الهيدر ====== */
    .hero {
        background: linear-gradient(135deg, #0a4d3a 0%, #0d6b4f 50%, #17a077 100%);
        border-radius: 20px;
        padding: 32px 36px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -20px rgba(10,77,58,.5);
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -50%; right: -10%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,.08), transparent 70%);
        border-radius: 50%;
    }
    .hero-title {
        color: #fff;
        font-size: 28px;
        font-weight: 800;
        margin: 0 0 6px;
        letter-spacing: -0.3px;
    }
    .hero-sub {
        color: #b8e0d1;
        font-size: 14px;
        margin: 0;
        font-weight: 500;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,.15);
        color: #fff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin-top: 14px;
        border: 1px solid rgba(255,255,255,.2);
    }

    /* ====== بطاقات الإحصائيات ====== */
    .stat-card {
        background: #fff;
        border: 1px solid #e8eeea;
        border-radius: 16px;
        padding: 20px;
        text-align: right;
        transition: .2s;
        height: 100%;
        box-shadow: 0 1px 3px rgba(16,40,32,.04);
    }
    .stat-card:hover {
        border-color: #c9dbd1;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -10px rgba(13,107,79,.2);
    }
    .stat-icon {
        width: 40px; height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-bottom: 12px;
    }
    .stat-icon.green { background: #e3f5ec; }
    .stat-icon.blue { background: #e5eefb; }
    .stat-icon.amber { background: #fdf2dc; }
    .stat-icon.purple { background: #f0e8fa; }
    .stat-label {
        font-size: 12.5px;
        color: #6b8079;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .stat-value {
        font-size: 30px;
        font-weight: 800;
        color: #14231f;
        line-height: 1;
        letter-spacing: -0.5px;
    }
    .stat-value.green { color: #0d6b4f; }
    .stat-value.amber { color: #c08a1a; }
    .stat-value.blue { color: #2563a8; }

    /* ====== بطاقة اليوم ====== */
    .day-header {
        background: #fff;
        border-radius: 16px 16px 0 0;
        padding: 18px 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #e8eeea;
        border-bottom: none;
        margin-top: 12px;
    }
    .day-header.done {
        background: linear-gradient(135deg, #f0f9f4, #e3f5ec);
        border-color: #c9dbd1;
    }
    .day-title {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .day-num {
        width: 40px; height: 40px;
        background: #e3f5ec;
        color: #0d6b4f;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 17px;
        font-weight: 800;
    }
    .day-header.done .day-num {
        background: #0d6b4f;
        color: #fff;
    }
    .day-name {
        font-size: 18px;
        font-weight: 800;
        color: #14231f;
        line-height: 1.2;
    }
    .day-meta {
        font-size: 12.5px;
        color: #6b8079;
        margin-top: 3px;
        font-weight: 600;
    }
    .day-status {
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 800;
        background: #eef2ef;
        color: #6b8079;
    }
    .day-status.done {
        background: #0d6b4f;
        color: #fff;
    }

    /* ====== شرائح المقرر والمشاركين ====== */
    .chips-row {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 6px;
    }
    .chip {
        background: #e7f3ee;
        color: #0d6b4f;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
    }
    .chip.gold {
        background: #fdf6e4;
        color: #a87a17;
    }
    .chip.gray {
        background: #f2f6f4;
        color: #8a9a94;
        font-weight: 600;
    }

    /* ====== Sidebar ====== */
    section[data-testid="stSidebar"] {
        background: #fff !important;
        border-left: 1px solid #e8eeea;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }
    .sidebar-title {
        font-size: 15px;
        font-weight: 800;
        color: #14231f;
        margin: 0 0 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e3f5ec;
    }

    /* ====== الأزرار ====== */
    .stButton > button {
        font-family: 'Tajawal', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        transition: .15s !important;
        border: 1px solid #e0e8e3 !important;
        direction: rtl !important;
    }
    .stButton > button:hover {
        border-color: #0d6b4f !important;
        color: #0d6b4f !important;
    }
    .stButton > button[kind="primary"] {
        background: #0d6b4f !important;
        color: #fff !important;
        border: none !important;
    }

    /* ====== المدخلات ====== */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        direction: rtl !important;
        text-align: right !important;
        border-radius: 10px !important;
        font-family: 'Tajawal', sans-serif !important;
    }
    .stMultiSelect [data-baseweb="select"] {
        direction: rtl;
    }
    div[data-baseweb="tag"] {
        background: #e3f5ec !important;
        color: #0d6b4f !important;
        font-weight: 700;
    }

    /* ====== Expander ====== */
    .streamlit-expanderHeader {
        background: #fafcfb;
        border-radius: 10px;
        font-weight: 700;
        direction: rtl;
        text-align: right;
    }

    /* ====== Tabs ====== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f4f7f5;
        padding: 5px;
        border-radius: 12px;
        direction: rtl;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 700;
        font-family: 'Tajawal', sans-serif;
    }

    /* ====== تحسين عرض الجوال ====== */
    @media (max-width: 768px) {
        .hero { padding: 22px 20px; }
        .hero-title { font-size: 20px; }
        .stat-value { font-size: 24px; }
        .day-name { font-size: 16px; }
    }
</style>
""", unsafe_allow_html=True)


# ==================================================
# 3) قاعدة البيانات
# ==================================================
DB_PATH = os.path.join("data", "quran_circle.db")

def get_conn():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                members TEXT NOT NULL DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS days (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_index INTEGER UNIQUE,
                day_name TEXT NOT NULL,
                assign TEXT NOT NULL DEFAULT '[]',
                assign_note TEXT DEFAULT '',
                attendees TEXT NOT NULL DEFAULT '[]',
                done INTEGER DEFAULT 0
            );
        """)
        days = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء"]
        for i, name in enumerate(days):
            conn.execute("INSERT OR IGNORE INTO days (day_index, day_name) VALUES (?, ?)", (i, name))
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('session_limit', '30')")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('completed_total', '0')")
        conn.commit()

init_db()


# ==================================================
# 4) دوال مساعدة
# ==================================================
def get_setting(key, default="0"):
    row = get_conn().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default

def set_setting(key, value):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()

def get_days():
    return get_conn().execute("SELECT * FROM days ORDER BY day_index").fetchall()

def get_groups():
    return get_conn().execute("SELECT * FROM groups ORDER BY id").fetchall()

def add_group(name, members_list):
    conn = get_conn()
    conn.execute("INSERT INTO groups (name, members) VALUES (?, ?)",
                 (name, json.dumps(members_list, ensure_ascii=False)))
    conn.commit()

def delete_group(gid):
    conn = get_conn()
    conn.execute("DELETE FROM groups WHERE id=?", (gid,))
    conn.commit()

def remove_member(gid, member_name):
    conn = get_conn()
    row = conn.execute("SELECT members FROM groups WHERE id=?", (gid,)).fetchone()
    if row:
        members = json.loads(row["members"])
        members = [m for m in members if m != member_name]
        conn.execute("UPDATE groups SET members=? WHERE id=?",
                     (json.dumps(members, ensure_ascii=False), gid))
        conn.commit()

def get_all_members():
    out = []
    for g in get_groups():
        for m in json.loads(g["members"]):
            out.append({"name": m, "group": g["name"], "group_id": g["id"]})
    return out


# ==================================================
# 5) الهيدر
# ==================================================
completed = int(get_setting("completed_total", "0"))
limit_val = int(get_setting("session_limit", "30"))
left = max(limit_val - completed, 0)
pct = min(100, round(completed / limit_val * 100)) if limit_val else 0
days_done = sum(1 for d in get_days() if d["done"])

st.markdown(f"""
<div class="hero">
    <h1 class="hero-title">📖 نظام إدارة الحلقة القرآنية</h1>
    <p class="hero-sub">تخطيط الدروس ومتابعة الجلسات — من السبت إلى الأربعاء</p>
    <span class="hero-badge">📅 {days_done} من 5 أيام مكتملة هذا الأسبوع</span>
</div>
""", unsafe_allow_html=True)


# ==================================================
# 6) بطاقات الإحصائيات
# ==================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon green">✅</div>
        <div class="stat-label">الجلسات المكتملة</div>
        <div class="stat-value green">{completed}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon blue">🎯</div>
        <div class="stat-label">حدّ الجلسات</div>
        <div class="stat-value blue">{limit_val}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon amber">⏳</div>
        <div class="stat-label">الجلسات المتبقية</div>
        <div class="stat-value amber">{left}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon purple">📊</div>
        <div class="stat-label">نسبة الإنجاز</div>
        <div class="stat-value">{pct}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 14px'></div>", unsafe_allow_html=True)
st.progress(pct / 100)


# ==================================================
# 7) الشريط الجانبي
# ==================================================
with st.sidebar:
    st.markdown('<p class="sidebar-title">⚙️ إعدادات الفصل</p>', unsafe_allow_html=True)

    current_limit = int(get_setting("session_limit", "30"))
    limit = st.number_input("حدّ الجلسات الكلي", min_value=1, max_value=500,
                            value=current_limit, key="limit_input")
    if limit != current_limit:
        set_setting("session_limit", limit)
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown('<p class="sidebar-title">👥 إنشاء مجموعة</p>', unsafe_allow_html=True)
    with st.form("new_group_form", clear_on_submit=True):
        g_name = st.text_input("اسم المجموعة", placeholder="مثال: مجموعة النور")
        g_members = st.text_area("الأسماء (سطر لكل اسم)",
                                  placeholder="عبد الله محمد\nيوسف أحمد\nخالد سعيد",
                                  height=110)
        if st.form_submit_button("➕ إنشاء المجموعة", use_container_width=True, type="primary"):
            if not g_name.strip():
                st.error("أدخل اسم المجموعة")
            else:
                members = [m.strip() for m in g_members.split("\n") if m.strip()]
                add_group(g_name.strip(), members)
                st.success(f"تم إنشاء «{g_name}»")
                st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">📋 المجموعات الحالية</p>', unsafe_allow_html=True)

    groups = get_groups()
    if groups:
        for g in groups:
            members = json.loads(g["members"])
            with st.expander(f"👥 {g['name']} — {len(members)}"):
                if members:
                    for m in members:
                        col_a, col_b = st.columns([5, 1])
                        with col_a:
                            st.markdown(f"• {m}")
                        with col_b:
                            if st.button("✕", key=f"rm_{g['id']}_{m}", help="حذف"):
                                remove_member(g["id"], m)
                                st.rerun()
                else:
                    st.caption("لا يوجد أعضاء")

                if st.button("🗑 حذف المجموعة", key=f"del_g_{g['id']}",
                             use_container_width=True):
                    delete_group(g["id"])
                    st.rerun()
    else:
        st.info("لا توجد مجموعات بعد")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">📋 القائمة الشاملة</p>', unsafe_allow_html=True)

    all_members = get_all_members()
    if all_members:
        st.caption(f"إجمالي المسجّلين: {len(all_members)}")
        for m in all_members:
            st.markdown(
                f"<div style='padding:6px 10px;background:#fafcfb;border-radius:8px;"
                f"margin-bottom:4px;font-size:13px'>"
                f"<b>{m['name']}</b> <span style='color:#8a9a94;font-size:11px'>"
                f"— {m['group']}</span></div>",
                unsafe_allow_html=True
            )
    else:
        st.info("لا يوجد مسجّلون بعد")


# ==================================================
# 8) التقويم الأسبوعي
# ==================================================
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.markdown("### 📅 التقويم الأسبوعي")
st.caption("خمسة أيام — من السبت إلى الأربعاء")

day_rows = get_days()
all_groups = get_groups()

available_members = []
for g in all_groups:
    for m in json.loads(g["members"]):
        available_members.append(m)

# خريطة العضو → مجموعته
member_group_map = {}
for g in all_groups:
    for m in json.loads(g["members"]):
        member_group_map[m] = g["name"]

for idx, day in enumerate(day_rows, 1):
    assign = json.loads(day["assign"])
    attendees = json.loads(day["attendees"])
    is_done = bool(day["done"])

    # ====== رأس البطاقة ======
    meta_parts = []
    if assign:
        meta_parts.append(f"{len(assign)} مقرر")
    if attendees:
        meta_parts.append(f"{len(attendees)} مشارك")
    meta = " · ".join(meta_parts) if meta_parts else "لم يُحدد بعد"

    st.markdown(f"""
    <div class="day-header {'done' if is_done else ''}">
        <div class="day-title">
            <div class="day-num">{idx}</div>
            <div>
                <div class="day-name">{day['day_name']}</div>
                <div class="day-meta">{meta}</div>
            </div>
        </div>
        <div class="day-status {'done' if is_done else ''}">
            {'✓ مكتملة' if is_done else 'متبقية'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ====== محتوى البطاقة ======
    with st.expander("تعديل التفاصيل", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📚 المقرر القرآني**")
            default_juz = [a["num"] for a in assign if a.get("kind") == "juz"]
            juz = st.multiselect(
                "اختر الأجزاء",
                options=list(range(1, 31)),
                default=default_juz,
                format_func=lambda x: f"الجزء {x}",
                key=f"juz_{day['id']}"
            )
            note = st.text_input(
                "ملاحظة على المقرر",
                value=day["assign_note"] or "",
                placeholder="مثال: من الآية ١ إلى ٢٠",
                key=f"note_{day['id']}"
            )

        with col2:
            st.markdown("**👥 المشاركون**")
            if available_members:
                default_att = [a for a in attendees if a in available_members]
                selected = st.multiselect(
                    "اختر المشاركين",
                    options=available_members,
                    default=default_att,
                    format_func=lambda x: f"{x} — {member_group_map.get(x, '')}",
                    key=f"att_{day['id']}"
                )
            else:
                st.info("لا يوجد مسجّلون")
                selected = []

        b1, b2 = st.columns(2)
        with b1:
            if st.button("💾 حفظ", key=f"save_{day['id']}",
                         use_container_width=True, type="primary"):
                new_assign = [{"kind": "juz", "num": n} for n in juz]
                conn = get_conn()
                conn.execute(
                    "UPDATE days SET assign=?, assign_note=?, attendees=? WHERE id=?",
                    (json.dumps(new_assign, ensure_ascii=False), note,
                     json.dumps(selected, ensure_ascii=False), day["id"])
                )
                conn.commit()
                st.success("✅ تم الحفظ")
                st.rerun()

        with b2:
            btn_label = "↩️ تراجع" if is_done else "✅ إتمام الجلسة"
            if st.button(btn_label, key=f"done_{day['id']}", use_container_width=True):
                conn = get_conn()
                new_done = 0 if is_done else 1
                conn.execute("UPDATE days SET done=? WHERE id=?", (new_done, day["id"]))
                conn.commit()
                diff = -1 if is_done else 1
                set_setting("completed_total", completed + diff)
                st.rerun()

    # شرائح العرض تحت البطاقة
    if assign or attendees:
        chips_html = '<div class="chips-row" style="padding: 0 4px 12px">'
        for a in assign:
            chips_html += f'<span class="chip gold">📖 الجزء {a["num"]}</span>'
        if day["assign_note"]:
            chips_html += f'<span class="chip gold">📝 {day["assign_note"]}</span>'
        for a in attendees:
            chips_html += f'<span class="chip">👤 {a}</span>'
        chips_html += '</div>'
        st.markdown(chips_html, unsafe_allow_html=True)


# ==================================================
# 9) أزرار الإدارة السفلية
# ==================================================
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.divider()

col_a, col_b, col_c = st.columns([1, 1, 2])

with col_a:
    if st.button("🔄 بدء أسبوع جديد", use_container_width=True):
        conn = get_conn()
        conn.execute("UPDATE days SET done=0")
        conn.commit()
        st.rerun()

with col_b:
    if st.button("♻️ إعادة تعيين الكل", use_container_width=True):
        conn = get_conn()
        conn.execute("UPDATE days SET done=0, assign='[]', attendees='[]', assign_note=''")
        conn.execute("UPDATE settings SET value='0' WHERE key='completed_total'")
        conn.commit()
        st.rerun()

with col_c:
    st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
