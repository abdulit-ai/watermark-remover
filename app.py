import io
import numpy as np
from PIL import Image
import streamlit as st
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates

# 1. Page Config
st.set_page_config(page_title="EzRemove Pro", layout="centered")

# 2. Premium SaaS CSS (Midnight Navy & Cyan)
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    /* Hide File Uploader after use */
    [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderSize"], 
    [data-testid="stFileUploaderDeleteBtn"], .uploadedFile { display: none !important; }
    
    /* Modern Navbar */
    .nav-container { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; margin-bottom: 2rem; }
    .logo-spiral {
        width: 35px; height: 35px;
        border: 4px solid rgba(56, 189, 248, 0.2);
        border-top: 4px solid #38bdf8;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    
    /* Clean Editor Layout */
    .stButton>button {
        background: #38bdf8; color: #0f172a !important; border-radius: 8px;
        border: none; padding: 10px; font-weight: 800; transition: 0.2s;
    }
    .stButton>button:hover { background: #7dd3fc; transform: translateY(-1px); }
    
    div[data-testid="stFileUploader"] {
        border: 2px dashed #38bdf8 !important; background: #1e293b !important;
        border-radius: 20px !important; padding: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Persistent State
if 'points' not in st.session_state:
    st.session_state.points = []
if 'result_img' not in st.session_state:
    st.session_state.result_img = None

# Navbar
st.markdown("""
    <div class="nav-container">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div class="logo-spiral"></div>
            <span style="font-size: 24px; font-weight: 900; color: #f8fafc;">EzRemove</span>
        </div>
        <div style="font-size: 14px; font-weight: 600; color: #38bdf8;">PRO AI MODE</div>
    </div>
    """, unsafe_allow_html=True)

# 4. Routing Logic (Home vs Editor)
if not st.session_state.get('uploaded_file_data'):
    # HOME PAGE - ONLY UPLOAD
    st.markdown("<h1 style='text-align: center;'>AI Watermark Remover</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 30px;'>Professional-grade pixel restoration in seconds.</p>", unsafe_allow_html=True)
    
    file = st.file_uploader("", type=["jpg", "png", "jpeg"], key="uploader")
    if file:
        st.session_state.uploaded_file_data = file
        st.rerun()
else:
    # EDITOR PAGE - IMAGE IS UPLOADED
    img_pil = Image.open(st.session_state.uploaded_file_data).convert("RGB")
    img_array = np.array(img_pil)
    
    # Header Tools
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        brush = st.select_slider("Brush Size", options=[15, 30, 50, 80], value=30)
    with c2:
        st.write("") # Spacer
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
        st.write("") # Spacer
        if st.button("🔄 EXIT"):
            st.session_state.uploaded_file_data = None
            st.session_state.points = []
            st.session_state.result_img = None
            st.rerun()

    # Display Workspace
    if st.session_state.result_img:
        st.image(st.session_state.result_img, use_container_width=True)
        buf = io.BytesIO()
        st.session_state.result_img.save(buf, format="PNG")
        st.download_button("Download Result", buf.getvalue(), "cleaned.png")
    else:
        # Draw transparent preview circles
        display_img = img_array.copy()
        for p in st.session_state.points:
            cv2.circle(display_img, p, brush, (56, 189, 248), -1)
        
        # Click interface
        out = streamlit_image_coordinates(Image.fromarray(display_img), key="ez_editor")
        if out:
            st.session_state.points.append((out['x'], out['y']))
            st.rerun()
