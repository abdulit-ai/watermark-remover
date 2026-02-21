import io
import numpy as np
from PIL import Image
import streamlit as st
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates

# 1. Page Config
st.set_page_config(page_title="EzRemove", layout="centered")

# 2. Professional Slate Theme CSS
st.markdown("""
    <style>
    /* Professional Slate Background (Not black, not white) */
    .stApp { 
        background-color: #1e293b !important; 
        color: #f8fafc !important;
    }
    
    /* Hide the file info and list entirely */
    [data-testid="stFileUploaderFileName"], 
    [data-testid="stFileUploaderSize"], 
    [data-testid="stFileUploaderDeleteBtn"],
    .uploadedFile { display: none !important; }

    /* Modern Navbar */
    .nav { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; margin-bottom: 20px; }
    
    /* Spiral Logo */
    .spiral-box { 
        width: 40px; height: 40px; 
        background: linear-gradient(45deg, #38bdf8, #818cf8); 
        border-radius: 12px; display: flex; align-items: center; justify-content: center; 
    }
    .spiral-inner { 
        width: 18px; height: 18px; border: 2px solid white; 
        border-top: 2px solid transparent; border-radius: 50%; 
        animation: spin 1s linear infinite; 
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    
    /* Custom High-End Buttons */
    .stButton>button { 
        background: #38bdf8; color: #0f172a; border-radius: 10px; 
        width: 100%; border: none; padding: 10px; font-weight: 800;
        transition: 0.2s;
    }
    .stButton>button:hover { background: #7dd3fc; color: #0f172a; }

    /* File Uploader Box */
    div[data-testid="stFileUploader"] { 
        border: 2px dashed #38bdf8 !important; 
        background: #334155 !important; 
        border-radius: 15px !important;
        padding: 20px;
    }
    
    /* Fix for coordinates tool visibility */
    .stImage { border-radius: 10px; border: 4px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# Navbar
st.markdown("""
    <div class="nav">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="spiral-box"><div class="spiral-inner"></div></div>
            <span style="font-size: 24px; font-weight: 800; color: #f1f5f9;">EzRemove</span>
        </div>
        <div style="font-size: 14px; font-weight: 600;">
            <span style="color: #38bdf8; border: 1px solid #38bdf8; padding: 6px 14px; border-radius: 20px;">AI POWERED</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if 'points' not in st.session_state:
    st.session_state.points = []
if 'result_img' not in st.session_state:
    st.session_state.result_img = None

uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    # Load Image
    img_pil = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(img_pil)
    
    # UI Controls
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        brush_size = st.select_slider("Brush Size", options=[15, 30, 50, 80], value=30)
    with c2:
        st.write("") 
        if st.button("✨ ERASE"):
            if st.session_state.points:
                mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
                for p in st.session_state.points:
                    cv2.circle(mask, p, brush_size, 255, -1)
                
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

    # Workspace
    if st.session_state.result_img:
        st.image(st.session_state.result_img, use_container_width=True)
        buf = io.BytesIO()
        st.session_state.result_img.save(buf, format="PNG")
        st.download_button("Download Result", buf.getvalue(), "ez_cleaned.png")
    else:
        # Create display version with markers
        display_img = img_array.copy()
        for p in st.session_state.points:
            cv2.circle(display_img, p, brush_size, (56, 189, 248), -1)
        
        # Display interaction tool
        # We pass the PIL object directly to ensure it renders
        out = streamlit_image_coordinates(Image.fromarray(display_img), key="ez_editor_final")
        
        if out:
            st.session_state.points.append((out['x'], out['y']))
            st.rerun()
else:
    st.session_state.points = []
    st.session_state.result_img = None
    st.markdown("<h4 style='text-align: center; margin-top: 60px; color: #94a3b8;'>Drop image here to begin</h4>", unsafe_allow_html=True)
