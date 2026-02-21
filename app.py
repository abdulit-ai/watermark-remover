import io
import numpy as np
from PIL import Image
import streamlit as st
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates

# 1. Page Config
st.set_page_config(page_title="EzRemove Pro", layout="centered")

# 2. Modern Midnight CSS (Improved Colors & Circle Loader)
st.markdown("""
    <style>
    /* Midnight Navy Theme */
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    /* Hide File Uploader clutter */
    [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderSize"], 
    [data-testid="stFileUploaderDeleteBtn"], .uploadedFile { display: none !important; }
    
    /* Neon Spiral Logo */
    .logo-box { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
    .circle-loader {
        width: 35px; height: 35px;
        border: 4px solid rgba(56, 189, 248, 0.2);
        border-top: 4px solid #38bdf8;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    
    /* Custom Modern Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        color: #0f172a !important; border-radius: 12px;
        border: none; padding: 12px; font-weight: 800; font-size: 16px;
        transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(56, 189, 248, 0.4); color: #0f172a !important; }

    /* Custom File Uploader */
    div[data-testid="stFileUploader"] {
        border: 2px dashed #38bdf8 !important; background: #1e293b !important;
        border-radius: 20px !important; padding: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# Navbar
st.markdown("""
    <div class="logo-box">
        <div class="circle-loader"></div>
        <span style="font-size: 26px; font-weight: 900; color: #f8fafc; letter-spacing: -1px;">EzRemove</span>
    </div>
    """, unsafe_allow_html=True)

# 3. State Management
if 'points' not in st.session_state:
    st.session_state.points = []
if 'result_img' not in st.session_state:
    st.session_state.result_img = None

# 4. Workspace Logic
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    # Use Fragments to prevent the whole page from "flashing" on every click
    @st.fragment
    def editor_workspace(file):
        img_pil = Image.open(file).convert("RGB")
        img_array = np.array(img_pil)
        
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            brush = st.select_slider("Brush Size", options=[15, 30, 50, 80], value=30)
        with c2:
            st.write("")
            if st.button("✨ ERASE"):
                if st.session_state.points:
                    mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
                    for p in st.session_state.points:
                        cv2.circle(mask, p, brush, 255, -1)
                    
                    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    res_bgr = cv2.inpaint(img_bgr, mask, 3, cv2.INPAINT_TELEA)
                    res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                    st.session_state.result_img = Image.fromarray(res_rgb)
                    st.session_state.points = []
                    st.rerun()
        with c3:
            st.write("")
            if st.button("🔄 RESET"):
                st.session_state.points = []
                st.session_state.result_img = None
                st.rerun()

        # Display Section
        if st.session_state.result_img:
            st.image(st.session_state.result_img, use_container_width=True)
            buf = io.BytesIO()
            st.session_state.result_img.save(buf, format="PNG")
            st.download_button("Download Result", buf.getvalue(), "ez_clean.png")
        else:
            # Draw markers on display
            display_img = img_array.copy()
            for p in st.session_state.points:
                cv2.circle(display_img, p, brush, (56, 189, 248), -1)
            
            # Interactive Area
            out = streamlit_image_coordinates(Image.fromarray(display_img), key="ez_editor")
            if out:
                st.session_state.points.append((out['x'], out['y']))
                st.rerun()

    editor_workspace(uploaded_file)
else:
    st.session_state.points = []
    st.session_state.result_img = None
    st.markdown("<div style='text-align: center; margin-top: 80px; color: #64748b;'><h3>Ready for Restoration</h3><p>Drop an image here to unlock AI Eraser</p></div>", unsafe_allow_html=True)
