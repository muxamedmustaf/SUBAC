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
# 2) التنسيقات الاحترافية
# ==================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px; }

    html, body, [class*="css"], .stApp {
        font-family: 'Tajawal', -apple-system, sans-serif !important;
        direction: rtl;
    }
    .stApp { background: #f4f7f5; }
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, div {
        direction: rtl;
        text-align: right;
    }

    /* ====== Hero ====== */
    .hero {
        background: linear-gradient(135deg, #0a4d3a 0%, #0d6b4f 50%, #17a077 100%);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 20px;
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
        color: #fff; font-size: 26px; font-weight: 800;
        margin: 0 0 6px; letter-spacing: -0.3px;
    }
    .hero-sub { color: #b8e0d1; font-size: 13.5px; margin: 0; font-weight: 500; }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,.15);
        color: #fff; padding: 6px 14px;
        border-radius: 20px; font-size: 12px; font-weight: 700;
        margin-top: 12px; border: 1px solid rgba(255,255,255,.2);
    }

    /* ====== Stat Cards ====== */
    .stat-card {
        background: #fff;
        border: 1px solid #e8eeea;
        border-radius: 16px;
        padding: 18px;
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
        width: 38px; height: 38px; border-radius: 11px;
        display: flex; align-items: center; justify-content: center;
        font-size: 19px; margin-bottom: 10px;
    }
    .stat-icon.green { background: #e3f5ec; }
    .stat-icon.blue { background: #e5eefb; }
    .stat-icon.amber { background: #fdf2dc; }
    .stat-icon.purple { background: #f0e8fa; }
    .stat-label { font-size: 12px; color: #6b8079; font-weight: 600; margin-bottom: 5px; }
    .stat-value {
        font-size: 28px; font-weight: 800; color: #14231f;
        line-height: 1; letter-spacing: -0.5px;
    }
    .stat-value.green { color: #0d6b4f; }
    .stat-value.amber { color: #c08a1a; }
    .stat-value.blue { color: #2563a8; }

    /* ====== Day Header ====== */
    .day-header {
        background: #fff;
        border-radius: 16px;
        padding: 16px 20px;
        display: flex; align-items: center; justify-content: space-between;
        border: 1px solid #e8eeea;
        margin-top: 10px;
        margin-bottom: 4px;
    }
    .day-header.done {
        background: linear-gradient(135deg, #f0f9f4, #e3f5ec);
        border-color: #a8d5bf;
    }
    .day-title { display: flex; align-items: center; gap: 12px; }
    .day-num {
        width: 42px; height: 42px;
        background: #e3f5ec; color: #0d6b4f;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 17px; font-weight: 800; flex: none;
    }
    .day-header.done .day-num { background: #0d6b4f; color: #fff; }
    .day-name { font-size: 17px; font-weight: 800; color: #14231f; line-height: 1.2; }
    .day-meta { font-size: 12px; color: #6b8079; margin-top: 3px; font-weight: 600; }
    .day-status {
        padding: 6px 14px; border-radius: 20px;
        font-size: 11.5px; font-weight: 800;
        background: #eef2ef; color: #6b8079;
    }
    .day-status.done { background: #0d6b4f; color: #fff; }

    /* ====== Chips ====== */
    .chips-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
    .chip {
        background: #e7f3ee; color: #0d6b4f;
        padding: 4px 12px; border-radius: 20px;
        font-size: 12px; font-weight: 700; display: inline-block;
    }
    .chip.gold { background: #fdf6e4; color: #a87a17; }
    .chip.gray { background: #f2f6f4; color: #8a9a94; font-weight: 600; }

    /* ====== Sidebar ====== */
    section[data-testid="stSidebar"] {
        background: #fff !important;
        border-left: 1px solid #e8eeea;
    }
    .sidebar-section {
        font-size: 14px; font-weight: 800; color: #14231f;
        margin: 14px 0 10px; padding-bottom: 8px;
        border-bottom: 2px solid #e3f5ec;
    }

    /* ====== Buttons ====== */
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
    .stButton > button[kind="primary"]:hover {
        background: #17a077 !important;
        color: #fff !important;
    }
    .stFormSubmitButton > button {
        font-family: 'Tajawal', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
    }

    /* ====== Inputs ====== */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        direction: rtl !important;
        text-align: right !important;
        border-radius: 10px !important;
        font-family: 'Tajawal', sans-serif !important;
    }
    div[data-baseweb="tag"] {
        background: #e3f5ec !important;
        color: #0d6b4f !important;
        font-weight: 700;
    }
    .streamlit-expanderHeader {
        font-weight: 700;
        direction: rtl;
        text-align: right;
    }

    /* ====== Member Row ====== */
    .member-row {
        display: flex; align-items: center; justify-content: space-between;
        background: #fafcfb; border: 1px solid #eef2ef;
        border-radius: 10px; padding: 8px 12px; margin-bottom: 5px;
    }
    .member-name { font-size: 13.5px; font-weight: 700; color: #14231f; }
    .member-group { font-size: 11px; color: #8a9a94; margin-right: 6px; }

    /* ====== Mobile ====== */
    @media (max-width: 768px) {
        .hero { padding: 20px 18px; }
        .hero-title { font-size: 19px; }
        .stat-value { font-size: 22px; }
        .day-name { font-size: 15px; }
        .day-header { padding: 12px 14px; }
        .day-num { width: 36px; height: 36px; font-size: 15px; }
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
# 4) دوال قاعدة البيانات
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

def get_group(gid):
    return get_conn().execute("SELECT * FROM groups WHERE id=?", (gid,)).fetchone()

def add_group(name, members_list):
    conn = get_conn()
    conn.execute("INSERT INTO groups (name, members) VALUES (?, ?)",
                 (name, json.dumps(members_list, ensure_ascii=False)))
    conn.commit()

def rename_group(gid, new_name):
    conn = get_conn()
    conn.execute("UPDATE groups SET name=? WHERE id=?", (new_name, gid))
    conn.commit()

def delete_group(gid):
    conn = get_conn()
    conn.execute("DELETE FROM groups WHERE id=?", (gid,))
    conn.commit()

def add_member(gid, member_name):
    conn = get_conn()
    row = conn.execute("SELECT members FROM groups WHERE id=?", (gid,)).fetchone()
    if not row:
        return False
    members = json.loads(row["members"])
    if member_name in members:
        return False
    members.append(member_name)
    conn.execute("UPDATE groups SET members=? WHERE id=?",
                 (json.dumps(members, ensure_ascii=False), gid))
    conn.commit()
    return True

def add_members_bulk(gid, names_list):
    conn = get_conn()
    row = conn.execute("SELECT members FROM groups WHERE id=?", (gid,)).fetchone()
    if not row:
        return 0
    members = json.loads(row["members"])
    added = 0
    for n in names_list:
        n = n.strip()
        if n and n not in members:
            members.append(n)
            added += 1
    conn.execute("UPDATE groups SET members=? WHERE id=?",
                 (json.dumps(members, ensure_ascii=False), gid))
    conn.commit()
    return added

def remove_member(gid, member_name):
    conn = get_conn()
    row = conn.execute("SELECT members FROM groups WHERE id=?", (gid,)).fetchone()
    if not row:
        return
    members = json.loads(row["members"])
    members = [m for m in members if m != member_name]
    conn.execute("UPDATE groups SET members=? WHERE id=?",
                 (json.dumps(members, ensure_ascii=False), gid))
    conn.commit()

def rename_member(gid, old_name, new_name):
    conn = get_conn()
    row = conn.execute("SELECT members FROM groups WHERE id=?", (gid,)).fetchone()
    if not row:
        return False
    members = json.loads(row["members"])
    if old_name not in members:
        return False
    if new_name in members and new_name != old_name:
        return False
    members = [new_name if m == old_name else m for m in members]
    conn.execute("UPDATE groups SET members=? WHERE id=?",
                 (json.dumps(members, ensure_ascii=False), gid))
    conn.commit()
    # تحديث الأيام التي فيها العضو القديم
    days = get_days()
    for d in days:
        att = json.loads(d["attendees"])
        if old_name in att:
            att = [new_name if a == old_name else a for a in att]
            conn.execute("UPDATE days SET attendees=? WHERE id=?",
                         (json.dumps(att, ensure_ascii=False), d["id"]))
    conn.commit()
    return True

def move_member(from_gid, to_gid, member_name):
    if from_gid == to_gid:
        return False
    from_row = get_conn().execute("SELECT members FROM groups WHERE id=?", (from_gid,)).fetchone()
    to_row = get_conn().execute("SELECT members FROM groups WHERE id=?", (to_gid,)).fetchone()
    if not from_row or not to_row:
        return False
    from_members = json.loads(from_row["members"])
    to_members = json.loads(to_row["members"])
    if member_name not in from_members or member_name in to_members:
        return False
    from_members.remove(member_name)
    to_members.append(member_name)
    conn = get_conn()
    conn.execute("UPDATE groups SET members=? WHERE id=?",
                 (json.dumps(from_members, ensure_ascii=False), from_gid))
    conn.execute("UPDATE groups SET members=? WHERE id=?",
                 (json.dumps(to_members, ensure_ascii=False), to_gid))
    conn.commit()
    return True

def get_all_members():
    out = []
    for g in get_groups():
        for m in json.loads(g["members"]):
            out.append({"name": m, "group": g["name"], "group_id": g["id"]})
    return out

def reset_week():
    conn = get_conn()
    conn.execute("UPDATE days SET done=0")
    conn.commit()

def reset_all():
    conn = get_conn()
    conn.execute("UPDATE days SET done=0, assign='[]', attendees='[]', assign_note=''")
    conn.execute("UPDATE settings SET value='0' WHERE key='completed_total'")
    conn.execute("DELETE FROM groups")
    conn.commit()


# ==================================================
# 5) Hero Header
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
# 6) Statistics Cards
# ==================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon green">✅</div>
        <div class="stat-label">الجلسات المكتملة</div>
        <div class="stat-value green">{completed}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon blue">🎯</div>
        <div class="stat-label">حدّ الجلسات</div>
        <div class="stat-value blue">{limit_val}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon amber">⏳</div>
        <div class="stat-label">الجلسات المتبقية</div>
        <div class="stat-value amber">{left}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon purple">📊</div>
        <div class="stat-label">نسبة الإنجاز</div>
        <div class="stat-value">{pct}%</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.progress(pct / 100)


# ==================================================
# 7) الشريط الجانبي
# ==================================================
with st.sidebar:
    # --- إعدادات الفصل ---
    st.markdown('<p class="sidebar-section">⚙️ إعدادات الفصل</p>', unsafe_allow_html=True)
    current_limit = int(get_setting("session_limit", "30"))
    limit = st.number_input("حدّ الجلسات الكلي", min_value=1, max_value=500,
                            value=current_limit, key="limit_input")
    if limit != current_limit:
        set_setting("session_limit", limit)
        st.rerun()

    # --- إنشاء مجموعة ---
    st.markdown('<p class="sidebar-section">➕ إنشاء مجموعة</p>', unsafe_allow_html=True)
    with st.form("new_group_form", clear_on_submit=True):
        g_name = st.text_input("اسم المجموعة", placeholder="مثال: مجموعة النور")
        g_members = st.text_area("الأسماء (سطر لكل اسم)",
                                  placeholder="عبد الله محمد\nيوسف أحمد",
                                  height=90)
        if st.form_submit_button("إنشاء المجموعة", use_container_width=True, type="primary"):
            if not g_name.strip():
                st.error("أدخل اسم المجموعة")
            else:
                members = [m.strip() for m in g_members.split("\n") if m.strip()]
                add_group(g_name.strip(), members)
                st.success(f"تم إنشاء «{g_name}»")
                st.rerun()

    # --- المجموعات الحالية ---
    st.markdown('<p class="sidebar-section">👥 المجموعات</p>', unsafe_allow_html=True)
    groups = get_groups()

    if groups:
        for g in groups:
            members = json.loads(g["members"])
            with st.expander(f"👥 {g['name']} — {len(members)} عضو"):

                # قائمة الأعضاء + أزرار التعديل/الحذف/النقل
                if members:
                    for m in members:
                        col1, col2, col3 = st.columns([6, 1, 1])
                        with col1:
                            st.markdown(f"<div style='padding-top:6px;font-weight:600;font-size:13px'>• {m}</div>",
                                        unsafe_allow_html=True)
                        with col2:
                            if st.button("✏️", key=f"edit_{g['id']}_{m}", help="تعديل الاسم"):
                                st.session_state[f"editing_{g['id']}_{m}"] = True
                                st.rerun()
                        with col3:
                            if st.button("✕", key=f"rm_{g['id']}_{m}", help="حذف العضو"):
                                remove_member(g["id"], m)
                                st.rerun()

                        # إذا كان العضو في وضع التعديل
                        if st.session_state.get(f"editing_{g['id']}_{m}", False):
                            with st.form(f"edit_form_{g['id']}_{m}"):
                                new_name = st.text_input("الاسم الجديد", value=m,
                                                          key=f"nn_{g['id']}_{m}")
                                cc1, cc2 = st.columns(2)
                                with cc1:
                                    if st.form_submit_button("حفظ", use_container_width=True, type="primary"):
                                        if new_name.strip() and new_name.strip() != m:
                                            ok = rename_member(g["id"], m, new_name.strip())
                                            if ok:
                                                st.session_state[f"editing_{g['id']}_{m}"] = False
                                                st.success("تم التعديل")
                                                st.rerun()
                                            else:
                                                st.error("الاسم موجود مسبقًا")
                                        else:
                                            st.session_state[f"editing_{g['id']}_{m}"] = False
                                            st.rerun()
                                with cc2:
                                    if st.form_submit_button("إلغاء", use_container_width=True):
                                        st.session_state[f"editing_{g['id']}_{m}"] = False
                                        st.rerun()

                            # نقل العضو لمجموعة أخرى
                            other_groups = [(og["id"], og["name"]) for og in groups if og["id"] != g["id"]]
                            if other_groups:
                                with st.form(f"move_form_{g['id']}_{m}"):
                                    target = st.selectbox(
                                        "نقل إلى مجموعة",
                                        options=[og[0] for og in other_groups],
                                        format_func=lambda x: next(og[1] for og in other_groups if og[0] == x),
                                        key=f"mv_{g['id']}_{m}"
                                    )
                                    if st.form_submit_button("📤 نقل", use_container_width=True):
                                        if move_member(g["id"], target, m):
                                            st.session_state[f"editing_{g['id']}_{m}"] = False
                                            st.success("تم النقل")
                                            st.rerun()
                else:
                    st.caption("لا يوجد أعضاء بعد")

                st.markdown("<hr style='margin:10px 0;border:none;border-top:1px solid #eef2ef'>",
                            unsafe_allow_html=True)

                # --- إضافة عضو واحد ---
                with st.form(f"add_member_{g['id']}", clear_on_submit=True):
                    new_member = st.text_input("إضافة عضو", placeholder="اكتب الاسم...",
                                                label_visibility="collapsed",
                                                key=f"newm_{g['id']}")
                    if st.form_submit_button("➕ إضافة عضو", use_container_width=True):
                        if new_member.strip():
                            if add_member(g["id"], new_member.strip()):
                                st.success(f"تم إضافة «{new_member.strip()}»")
                                st.rerun()
                            else:
                                st.warning("الاسم موجود مسبقًا")
                        else:
                            st.error("أدخل اسمًا")

                # --- إضافة عدة أعضاء دفعة واحدة ---
                with st.form(f"bulk_add_{g['id']}", clear_on_submit=True):
                    bulk = st.text_area("إضافة دفعة", height=70,
                                         placeholder="اسم 1\nاسم 2\nاسم 3",
                                         label_visibility="collapsed",
                                         key=f"bulk_{g['id']}")
                    if st.form_submit_button("📥 إضافة دفعة", use_container_width=True):
                        if bulk.strip():
                            names = [n.strip() for n in bulk.split("\n") if n.strip()]
                            added = add_members_bulk(g["id"], names)
                            if added > 0:
                                st.success(f"تم إضافة {added} عضو")
                                st.rerun()
                            else:
                                st.warning("لم يُضف أحد (الأسماء موجودة)")
                        else:
                            st.error("أدخل أسماء")

                # --- تعديل اسم المجموعة ---
                with st.form(f"rename_g_{g['id']}", clear_on_submit=True):
                    new_g_name = st.text_input("تعديل اسم المجموعة",
                                                placeholder="الاسم الجديد...",
                                                label_visibility="collapsed",
                                                key=f"ngn_{g['id']}")
                    if st.form_submit_button("✏️ تعديل اسم المجموعة", use_container_width=True):
                        if new_g_name.strip():
                            rename_group(g["id"], new_g_name.strip())
                            st.success("تم التعديل")
                            st.rerun()

                # --- حذف المجموعة ---
                if st.button("🗑 حذف المجموعة كاملة", key=f"del_g_{g['id']}",
                             use_container_width=True):
                    delete_group(g["id"])
                    st.rerun()
    else:
        st.info("لا توجد مجموعات بعد — أنشئ أول مجموعة")

    # --- القائمة الشاملة ---
    st.markdown('<p class="sidebar-section">📋 القائمة الشاملة</p>', unsafe_allow_html=True)
    all_members = get_all_members()

    if all_members:
        st.caption(f"إجمالي المسجّلين: {len(all_members)}")

        search = st.text_input("🔍 بحث عن اسم", placeholder="اكتب للبحث...",
                                label_visibility="collapsed", key="master_search")

        filtered = [m for m in all_members if not search or search.strip() in m["name"]]

        if filtered:
            for m in filtered:
                st.markdown(
                    f"<div class='member-row'>"
                    f"<span><span class='member-name'>{m['name']}</span>"
                    f"<span class='member-group'>— {m['group']}</span></span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.caption("لا نتائج مطابقة")
    else:
        st.info("لا يوجد مسجّلون بعد")

    # --- أزرار الإدارة ---
    st.markdown('<p class="sidebar-section">🛠 إدارة</p>', unsafe_allow_html=True)

    if st.button("🔄 بدء أسبوع جديد", use_container_width=True):
        reset_week()
        st.success("أسبوع جديد")
        st.rerun()

    if st.button("♻️ إعادة تعيين كل شيء", use_container_width=True):
        reset_all()
        st.warning("تم حذف كل البيانات")
        st.rerun()

    st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# ==================================================
# 8) التقويم الأسبوعي
# ==================================================
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.markdown("### 📅 التقويم الأسبوعي")
st.caption("خمسة أيام — من السبت إلى الأربعاء")

day_rows = get_days()
available_members = []
member_group_map = {}
for g in get_groups():
    for m in json.loads(g["members"]):
        available_members.append(m)
        member_group_map[m] = g["name"]

for idx, day in enumerate(day_rows, 1):
    assign = json.loads(day["assign"])
    attendees = json.loads(day["attendees"])
    is_done = bool(day["done"])

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
                st.info("لا يوجد مسجّلون — أنشئ مجموعة أولًا")
                selected = []

        b1, b2, b3 = st.columns([1, 1, 1])

        with b1:
            if st.button("💾 حفظ التعديلات", key=f"save_{day['id']}",
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

        with b3:
            if st.button("🧹 مسح اليوم", key=f"clear_{day['id']}", use_container_width=True):
                conn = get_conn()
                conn.execute(
                    "UPDATE days SET assign='[]', assign_note='', attendees='[]' WHERE id=?",
                    (day["id"],)
                )
                conn.commit()
                st.rerun()

    # شرائح العرض
    if assign or attendees or day["assign_note"]:
        chips_html = '<div class="chips-row" style="padding: 0 4px 14px">'
        for a in assign:
            chips_html += f'<span class="chip gold">📖 الجزء {a["num"]}</span>'
        if day["assign_note"]:
            chips_html += f'<span class="chip gold">📝 {day["assign_note"]}</span>'
        for a in attendees:
            chips_html += f'<span class="chip">👤 {a}</span>'
        chips_html += '</div>'
        st.markdown(chips_html, unsafe_allow_html=True)
