import io
import numpy as np
from PIL import Image
import streamlit as st
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates

# 1. Page Config
st.set_page_config(page_title="EzRemove", layout="centered")

# 2. Fixed CSS (Background, Logo, and File Uploader)
st.markdown("""
    <style>
    /* Dark Modern Background */
    .stApp { 
        background-color: #0e1117 !important; 
        color: white !important;
    }
    
    /* Hide the ugly file list after upload */
    [data-testid="stFileUploaderDeleteBtn"] { display: none; }
    [data-testid="stFileUploaderFileName"] { display: none; }
    
    /* Modern Navbar */
    .nav { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; margin-bottom: 2rem; }
    
    /* Spiral Logo with actual color */
    .spiral-box { 
        width: 40px; height: 40px; 
        background: linear-gradient(45deg, #6c5ce7, #a29bfe); 
        border-radius: 10px; display: flex; align-items: center; justify-content: center; 
    }
    .spiral-inner { 
        width: 18px; height: 18px; border: 2px solid white; 
        border-top: 2px solid transparent; border-radius: 50%; 
        animation: spin 1s linear infinite; 
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    
    /* Custom Buttons */
    .stButton>button { 
        background: #6c5ce7; color: white; border-radius: 8px; 
        width: 100%; border: none; padding: 0.5rem; font-weight: bold;
    }
    .stButton>button:hover { background: #5849d1; border: none; color: white; }

    /* File Uploader Box */
    div[data-testid="stFileUploader"] { 
        border: 2px dashed #6c5ce7 !important; 
        background: #161b22 !important; 
        border-radius: 15px !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# Navbar
st.markdown("""
    <div class="nav">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="spiral-box"><div class="spiral-inner"></div></div>
            <span style="font-size: 22px; font-weight: 800; color: #ffffff;">EzRemove</span>
        </div>
        <div style="font-size: 14px; font-weight: 600;">
            <span style="color: #6c5ce7; background: rgba(108, 92, 231, 0.1); padding: 8px 16px; border-radius: 20px;">PRO MODE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if 'points' not in st.session_state:
    st.session_state.points = []
if 'result_img' not in st.session_state:
    st.session_state.result_img = None

uploaded_file = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    # Load Image
    original_pil = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(original_pil)
    
    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        brush_size = st.select_slider("Brush Size", options=[15, 30, 50, 70], value=30)
    with col_b:
        st.write("") 
        if st.button("✨ Erase"):
            if st.session_state.points:
                mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
                for p in st.session_state.points:
                    cv2.circle(mask, p, brush_size, 255, -1)
                
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                res_bgr = cv2.inpaint(img_bgr, mask, 5, cv2.INPAINT_TELEA) # Reduced radius for speed
                res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                st.session_state.result_img = Image.fromarray(res_rgb)
                st.session_state.points = []
                st.rerun()
    with col_c:
        st.write("") 
        if st.button("🔄 Reset"):
            st.session_state.points = []
            st.session_state.result_img = None
            st.rerun()

    # The Workspace
    if st.session_state.result_img:
        st.image(st.session_state.result_img, use_container_width=True)
        buf = io.BytesIO()
        st.session_state.result_img.save(buf, format="PNG")
        st.download_button("Download result", buf.getvalue(), "clean.png")
    else:
        # Draw transparent markers
        display_img = img_array.copy()
        for p in st.session_state.points:
            cv2.circle(display_img, p, brush_size, (108, 92, 231), -1)
        
        # Immediate image display
        value = streamlit_image_coordinates(Image.fromarray(display_img), key="edit_v3")
        
        if value:
            st.session_state.points.append((value['x'], value['y']))
            st.rerun()
else:
    st.session_state.points = []
    st.session_state.result_img = None
    st.markdown("<h3 style='text-align: center; margin-top: 50px; color: #636e72;'>Drop an image to start cleaning</h3>", unsafe_allow_html=True)
