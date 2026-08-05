import streamlit as st

st.set_page_config(page_title="Local Face Guard", page_icon="🛡️")

st.title("🛡️ Android Offline Face Guard")
st.write("Nidaamka amniga wajiga ee maxaliga ah (Local & Offline Mode).")

st.sidebar.header("Xakamaynta Amniga")
status = st.sidebar.selectbox("Xaaladda Moobilka:", ["Active (Mulkiilaha)", "Locked (Waji Qalaad)", "Setup Mode"])

if status == "Active (Mulkiilaha)":
    st.success("✅ Wajiga mulkiilaha waa la aqoonsaday. Shaashadu waa furnaan kartaa.")
elif status == "Locked (Waji Qalaad)":
    st.error("🚨 DIGNAAN: Waji aan la aqoon baa la helay! Moobilka waa la xiray.")
else:
    st.warning("⚙️ Nidaamku wuxuu ku jiraa diiwaangelinta wajiga (Local Storage).")
  
