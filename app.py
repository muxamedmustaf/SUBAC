import streamlit as st
import sqlite3
import os
import json
from datetime import datetime

# ==================================================
# 1) إعداد الصفحة ودعم العربية
# ==================================================
st.set_page_config(
    page_title="إدارة الحلقة القرآنية",
    page_icon="📖",
    layout="wide"
)

st.markdown("""
<style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', sans-serif;
    }
    .stApp { background: #eef2ef; }
    h1, h2, h3 { color: #0d6b4f; }
    .main-title {
        background: linear-gradient(120deg, #0b5c44, #12876a);
        color: #fff;
        padding: 20px 28px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 6px 24px -12px rgba(13,107,79,.7);
    }
    .main-title h1 { color: #fff; margin: 0; font-size: 24px; }
    .main-title p { color: #d7ece4; margin: 4px 0 0; font-size: 13px; }
    .metric-box {
        background: #fff;
        border: 1px solid #e0e8e3;
        border-radius: 14px;
        padding: 16px 18px;
        text-align: center;
        box-shadow: 0 1px 2px rgba(16,40,32,.05);
    }
    .metric-box .label { font-size: 12px; color: #6b8079; font-weight: 600; }
    .metric-box .value { font-size: 26px; font-weight: 800; color: #0d6b4f; margin-top: 6px; }
    .stButton > button {
        font-family: 'Tajawal', sans-serif;
        font-weight: 700;
        border-radius: 10px;
    }
    .stMultiSelect, .stTextInput, .stTextArea, .stNumberInput {
        direction: rtl;
        text-align: right;
    }
    section[data-testid="stSidebar"] { background: #f7fbf9; }
</style>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


# ==================================================
# 2) قاعدة البيانات (SQLite)
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
            conn.execute(
                "INSERT OR IGNORE INTO days (day_index, day_name) VALUES (?, ?)",
                (i, name)
            )
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('session_limit', '30')")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('completed_total', '0')")
        conn.commit()

init_db()


# ==================================================
# 3) دوال مساعدة
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
    conn.execute(
        "INSERT INTO groups (name, members) VALUES (?, ?)",
        (name, json.dumps(members_list, ensure_ascii=False))
    )
    conn.commit()

def delete_group(group_id):
    conn = get_conn()
    conn.execute("DELETE FROM groups WHERE id=?", (group_id,))
    conn.commit()

def get_all_members():
    """يرجع قائمة بكل الأسماء مع اسم المجموعة"""
    out = []
    for g in get_groups():
        for m in json.loads(g["members"]):
            out.append({"name": m, "group": g["name"]})
    return out


# ==================================================
# 4) الواجهة الرئيسية
# ==================================================
st.markdown("""
<div class="main-title">
    <h1>📖 نظام إدارة الحلقة القرآنية</h1>
    <p>تخطيط الدروس ومتابعة الجلسات — من السبت إلى الأربعاء</p>
</div>
""", unsafe_allow_html=True)


# ---------- الشريط الجانبي ----------
with st.sidebar:
    st.header("⚙️ الإعدادات")

    current_limit = int(get_setting("session_limit", "30"))
    limit = st.number_input(
        "حدّ الجلسات الكلي",
        min_value=1, max_value=500,
        value=current_limit,
        key="limit_input"
    )
    if limit != current_limit:
        set_setting("session_limit", limit)
        st.rerun()

    st.divider()
    st.header("👥 إنشاء مجموعة جديدة")

    with st.form("new_group_form", clear_on_submit=True):
        g_name = st.text_input("اسم المجموعة", placeholder="مثال: مجموعة النور")
        g_members = st.text_area(
            "الأسماء (سطر واحد لكل اسم)",
            placeholder="عبد الله محمد\nيوسف أحمد\nخالد سعيد",
            height=120
        )
        submitted = st.form_submit_button("➕ إنشاء المجموعة", use_container_width=True)

        if submitted:
            if not g_name.strip():
                st.error("أدخل اسم المجموعة")
            else:
                members = [m.strip() for m in g_members.split("\n") if m.strip()]
                add_group(g_name.strip(), members)
                st.success(f"تم إنشاء «{g_name}»")
                st.rerun()

    st.divider()
    st.header("📋 المجموعات الحالية")

    groups = get_groups()
    if groups:
        for g in groups:
            members = json.loads(g["members"])
            with st.expander(f"{g['name']} ({len(members)})"):
                if members:
                    for m in members:
                        st.write(f"• {m}")
                else:
                    st.caption("لا يوجد أعضاء")
                if st.button(f"🗑 حذف المجموعة", key=f"del_g_{g['id']}", use_container_width=True):
                    delete_group(g["id"])
                    st.rerun()
    else:
        st.info("لا توجد مجموعات بعد")

    st.divider()
    st.header("📋 القائمة الشاملة")
    all_members = get_all_members()
    if all_members:
        st.caption(f"إجمالي المسجّلين: {len(all_members)}")
        for m in all_members:
            st.write(f"• {m['name']} — _{m['group']}_")
    else:
        st.info("لا يوجد مسجّلون بعد")


# ---------- الإحصائيات ----------
completed = int(get_setting("completed_total", "0"))
limit_val = int(get_setting("session_limit", "30"))
left = max(limit_val - completed, 0)
pct = min(100, round(completed / limit_val * 100)) if limit_val else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="label">الجلسات المكتملة</div>
        <div class="value">{completed}</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="label">حدّ الجلسات</div>
        <div class="value">{limit_val}</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="label">الجلسات المتبقية</div>
        <div class="value">{left}</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="label">نسبة الإنجاز</div>
        <div class="value">{pct}%</div>
    </div>
    """, unsafe_allow_html=True)

st.progress(pct / 100)
st.write("")


# ---------- التقويم الأسبوعي ----------
st.subheader("📅 التقويم الأسبوعي")

day_rows = get_days()
all_groups = get_groups()

# جمع كل الأسماء المتاحة
available_members = []
for g in all_groups:
    for m in json.loads(g["members"]):
        available_members.append(m)

for day in day_rows:
    assign = json.loads(day["assign"])
    attendees = json.loads(day["attendees"])
    is_done = bool(day["done"])

    # عنوان البطاقة
    title = f"{'✅' if is_done else '📖'} **{day['day_name']}**"
    if assign:
        title += f"  ·  {len(assign)} مقرر"
    if attendees:
        title += f"  ·  {len(attendees)} مشارك"

    with st.expander(title, expanded=not is_done):
        col1, col2 = st.columns(2)

        # ----- المقرر القرآني -----
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
                "ملاحظة على المقرر (اختياري)",
                value=day["assign_note"] or "",
                placeholder="مثال: من الآية ١ إلى ٢٠",
                key=f"note_{day['id']}"
            )

        # ----- المشاركون -----
        with col2:
            st.markdown("**👥 المشاركون**")
            if available_members:
                default_att = [a for a in attendees if a in available_members]
                selected = st.multiselect(
                    "اختر المشاركين",
                    options=available_members,
                    default=default_att,
                    key=f"att_{day['id']}"
                )
            else:
                st.info("لا يوجد مسجّلون — أنشئ مجموعة أولًا")
                selected = []

        # ----- أزرار الحفظ -----
        b1, b2 = st.columns(2)

        with b1:
            if st.button("💾 حفظ التعديلات", key=f"save_{day['id']}", use_container_width=True):
                new_assign = [{"kind": "juz", "num": n} for n in juz]
                conn = get_conn()
                conn.execute(
                    "UPDATE days SET assign=?, assign_note=?, attendees=? WHERE id=?",
                    (
                        json.dumps(new_assign, ensure_ascii=False),
                        note,
                        json.dumps(selected, ensure_ascii=False),
                        day["id"]
                    )
                )
                conn.commit()
                st.success("✅ تم الحفظ")
                st.rerun()

        with b2:
            btn_label = "↩️ تراجع عن الإتمام" if is_done else "✅ تسجيل إتمام الجلسة"
            if st.button(btn_label, key=f"done_{day['id']}", use_container_width=True):
                conn = get_conn()
                new_done = 0 if is_done else 1
                conn.execute("UPDATE days SET done=? WHERE id=?", (new_done, day["id"]))
                conn.commit()
                diff = -1 if is_done else 1
                set_setting("completed_total", completed + diff)
                st.rerun()


# ==================================================
# 5) زر إعادة تعيين الأسبوع
# ==================================================
st.divider()
col_a, col_b, col_c = st.columns([1, 1, 2])

with col_a:
    if st.button("🔄 بدء أسبوع جديد", use_container_width=True):
        conn = get_conn()
        conn.execute("UPDATE days SET done=0")
        conn.commit()
        st.success("تم بدء أسبوع جديد (مع الحفاظ على إجمالي الجلسات المكتملة)")
        st.rerun()

with col_b:
    if st.button("♻️ إعادة تعيين كل شيء", use_container_width=True):
        conn = get_conn()
        conn.execute("UPDATE days SET done=0, assign='[]', attendees='[]', assign_note=''")
        conn.execute("UPDATE settings SET value='0' WHERE key='completed_total'")
        conn.commit()
        st.warning("تم إعادة تعيين جميع البيانات")
        st.rerun()

with col_c:
    st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
