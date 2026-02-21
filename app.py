import io
import numpy as np
from PIL import Image
import streamlit as st
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates
import time

# 1. Page Config
st.set_page_config(page_title="EzRemove | AI Editor", layout="centered")

# 2. Ultra-Modern CSS
st.markdown("""
    <style>
    .stApp { background: #ffffff; }
    
    /* Modern Navbar */
    .nav { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid #f0f0f0; margin-bottom: 2rem; }
    .spiral-box { width: 40px; height: 40px; background: #6c5ce7; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
    .spiral-inner { width: 18px; height: 18px; border: 2px solid white; border-top: 2px solid transparent; border-radius: 50%; animation: spin 2s linear infinite; }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    
    /* Glowing Progress Bar */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #6c5ce7 , #a29bfe);
        box-shadow: 0 0 15px rgba(108, 92, 231, 0.5);
    }
    
    /* File Uploader Style */
    div[data-testid="stFileUploader"] { border: 2px dashed #6c5ce7 !important; border-radius: 20px !important; background: #fafafa; }
    
    /* Button Styles */
    .stButton>button { 
        background: #1d1d1f; color: white; border-radius: 50px; width: 100%; border: none; 
        padding: 0.6rem; font-weight: 600; transition: 0.3s;
    }
    .stButton>button:hover { background: #6c5ce7; transform: translateY(-2px); color: white; }
    
    /* Remove streamlit padding */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# Navbar
st.markdown("""
    <div class="nav">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div class="spiral-box"><div class="spiral-inner"></div></div>
            <span style="font-size: 22px; font-weight: 800; color: #1d1d1f; letter-spacing: -0.5px;">EzRemove</span>
        </div>
        <div style="font-size: 14px; font-weight: 600; color: #636e72;">
            Login &nbsp;&nbsp; <span style="background: #1d1d1f; color: white; padding: 8px 20px; border-radius: 50px;">Sign Up</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Session State
if 'points' not in st.session_state:
    st.session_state.points = []
if 'result_img' not in st.session_state:
    st.session_state.result_img = None

uploaded_file = st.file_uploader("Drop an image to start cleaning", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Prepare Image
    original_pil = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(original_pil)
    
    # UI Controls
    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        brush_size = st.select_slider("Brush Size", options=[10, 20, 30, 40, 60, 80], value=30)
    with col_b:
        st.write("") # Padding
        erase_btn = st.button("✨ Erase")
    with col_c:
        st.write("") # Padding
        if st.button("🔄 Reset"):
            st.session_state.points = []
            st.session_state.result_img = None
            st.rerun()

    # Erase Logic with Modern Loading
    if erase_btn and st.session_state.points:
        progress_text = "AI is analyzing textures..."
        my_bar = st.progress(0, text=progress_text)
        
        # Simulate modern loading
        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1, text=progress_text)
        
        mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
        for p in st.session_state.points:
            cv2.circle(mask, p, brush_size, 255, -1)
        
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        res_bgr = cv2.inpaint(img_bgr, mask, 7, cv2.INPAINT_TELEA)
        res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
        st.session_state.result_img = Image.fromarray(res_rgb)
        st.session_state.points = []
        st.rerun()

    # Workspace
    if st.session_state.result_img:
        st.image(st.session_state.result_img, use_container_width=True)
        buf = io.BytesIO()
        st.session_state.result_img.save(buf, format="PNG")
        st.download_button("Download Clean HD Image", buf.getvalue(), "ezremove_final.png")
    else:
        # Drawing the semi-transparent overlay
        overlay = img_array.copy()
        for p in st.session_state.points:
            # Drawing a purple semi-transparent circle
            cv2.circle(overlay, p, brush_size, (108, 92, 231), -1)
        
        # Alpha blending to make selections semi-transparent
        alpha = 0.4
        display_img = cv2.addWeighted(overlay, alpha, img_array, 1 - alpha, 0)
        display_pil = Image.fromarray(display_img)
        
        st.markdown("<p style='color: #636e72; font-size: 14px;'>Click exactly on the watermark to mark it:</p>", unsafe_allow_html=True)
        
        # Display the interactive image
        value = streamlit_image_coordinates(display_pil, key="editor")
        
        if value:
            new_point = (value['x'], value['y'])
            if new_point not in st.session_state.points:
                st.session_state.points.append(new_point)
                st.rerun()
else:
    # Clean state
    st.session_state.points = []
    st.session_state.result_img = None
    st.markdown("<div style='text-align: center; margin-top: 100px;'><h2 style='color: #d1d1d1;'>No Image Uploaded</h2><p style='color: #e0e0e0;'>Select a file to begin the AI restoration process.</p></div>", unsafe_allow_html=True)
