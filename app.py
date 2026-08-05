import cv2
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="Local Face Guard", page_icon="🛡️", layout="centered"
)

st.title("🛡️ واقي وجه يعمل بدون اتصال بالإنترنت")
st.subheader("نظام حماية الخصوصية الشخصية (Anti-Snoop Privacy Guard)")

if "locked" not in st.session_state:
  st.session_state.locked = False

if st.session_state.locked:
  st.error(
      "🚨 DIGNIIN! Waji kale ama qof aan la aqoon ayaa la arkay! Shaashaddu waa"
      " la xiray si loo ilaaliyo sirtaada."
  )
  if st.button("🔓 Fur oo dib u billow (Unlock)"):
    st.session_state.locked = False
    st.rerun()
  st.stop()

st.info(
    "💡 Habraaca: Isticmaal kamaradda si aad u hubiso in adiga oo kaliya aad"
    " hortagto shaashadda."
)

camera_image = st.camera_input("Qaado sawir tijaabo ah si loo xaqiijiyo wajiga")

if camera_image is not None:
  bytes_data = camera_image.getvalue()
  np_arr = np.frombuffer(bytes_data, np.uint8)
  img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

  # Hubin fudud oo sawirka ah (Si uusan khalad u soo bixin)
  if img is not None:
    st.success("✅ Sawirka si guul leh ayaa loo qabtay waana la helay!")

    if st.button("🔒 Tijaabi Qufulka Degdegga ah (Simulate Threat)"):
      st.session_state.locked = True
      st.rerun()
        
