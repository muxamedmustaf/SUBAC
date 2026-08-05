import cv2
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="Local Face Guard", page_icon="🛡️", layout="centered"
)

st.title("🛡️ واقي وجه يعمل بدون اتصال بالإنترنت")
st.subheader("نظام حماية الخصوصية الشخصية (Anti-Snoop Privacy Guard)")

# Xaaladda amniga (Security State)
if "locked" not in st.session_state:
  st.session_state.locked = False

# Haddii uu app-ku xiran yahay sabab la xiriirta waji qarijiye
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

# Isticmaalka kamaradda taleefanka
camera_image = st.camera_input("Qaado sawir tijaabo ah si loo xaqiijiyo wajiga")

if camera_image is not None:
  # Akhriska sawirka iyadoo la adeegsanayo OpenCV
  bytes_data = camera_image.getvalue()
  np_arr = np.frombuffer(bytes_data, np.uint8)
  img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

  # Halkan waxaan ku isticmaali karnaa OpenCV Haar Cascade si aan u ogaanno wajiga
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  face_cascade = cv2.CascadeClassifier(
      cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
  )
  faces = face_cascade.detectMultiScale(
      gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
  )

  if len(faces) > 0:
    st.success(
        f"✅ Wajiga waa la helay! Tirada wajiyada la arkay: {len(faces)}. Xaaladdu"
        " waa ammaan."
    )
    # Halkan haddii aad rabto in la xaqiijiyo inuu yahay wajigaagii saxda ahaa (tusaale adigoo diiwaangeliyay sawirkaaga kowaad)
  else:
    st.warning("⚠️ Waji lama helin! Fadlan istaag horayna u eeg kamaradda.")

  # Tusaale badhan lagu tijaabiyo xiritaanka degrta ah (Privacy Lock Simulation)
  if st.button("🔒 Tijaabi Qufulka Degdegga ah (Simulate Threat)"):
    st.session_state.locked = True
    st.rerun()
      
