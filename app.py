import io
import numpy as np
from PIL import Image
import streamlit as st
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates

# Page Config
st.set_page_config(page_title="EzRemove | AI Editor", layout="centered")

# Modern CSS for a clean UI
st.markdown("""
    <style>
    .stApp { background: #ffffff; }
    .nav { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid #eee; margin-bottom: 2rem; }
    .spiral-box { width: 40px; height: 40px; background: #6c5ce7; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-right: 12px; }
    .spiral-inner { width: 18px; height: 18px; border: 2px solid white; border-top: 2px solid transparent; border-radius: 50%; animation: spin 2s linear infinite; }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    div[data-testid="stFileUploader"] { border: 2px dashed #6c5ce7 !important; border-radius: 15px !important; }
    .stButton>button { background: #1d1d1f; color: white; border-radius: 50px; width: 100%; border: none; padding: 0.5rem; }
    .stButton>button:hover { background: #6c5ce7; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# Navbar
st.markdown("""
    <div class="nav">
        <div style="display: flex; align-items: center;">
            <div class="spiral-box"><div class="spiral-inner"></div></div>
            <span style="font-size: 20px; font-weight: 700; color: #1d1d1f;">EzRemove</span>
        </div>
        <div style="font-size: 14px; font-weight: 500; color: #636e72;">Login &nbsp; | &nbsp; <span style="color: #6c5ce7;">Get Started</span></div>
    </div>
    """, unsafe_allow_html=True)

# Initialize Session States
if 'points' not in st.session_state:
    st.session_state.points = []
if 'result_img' not in st.session_state:
    st.session_state.result_img = None

uploaded_file = st.file_uploader("Upload an image to start cleaning", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 1. Load the original base image
    original_pil = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(original_pil)
    
    # 2. Controls Section
    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        brush_size = st.select_slider("Brush Precision", options=[10, 20, 30, 50, 80], value=30)
    with col_b:
        st.write("") # Spacer
        clean_clicked = st.button("✨ Erase")
    with col_c:
        st.write("") # Spacer
        if st.button("🔄 Reset"):
            st.session_state.points = []
            st.session_state.result_img = None
            st.rerun()

    # 3. Handle the "Cleaning" Logic
    if clean_clicked and st.session_state.points:
        with st.spinner("Removing..."):
            mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
            for p in st.session_state.points:
                cv2.circle(mask, p, brush_size, 255, -1)
            
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            res_bgr = cv2.inpaint(img_bgr, mask, 7, cv2.INPAINT_TELEA)
            res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
            st.session_state.result_img = Image.fromarray(res_rgb)
            st.session_state.points = [] # Clear selection after cleaning

    # 4. THE MAIN WORKSPACE
    # If we have a result, show it. Otherwise, show the interactive image.
    if st.session_state.result_img:
        st.image(st.session_state.result_img, use_container_width=True, caption="Restored Image")
        
        buf = io.BytesIO()
        st.session_state.result_img.save(buf, format="PNG")
        st.download_button("Download Cleaned Photo", buf.getvalue(), "cleaned.png")
    else:
        # Before showing the image, draw the circles on it so the user sees their clicks
        display_img_array = img_array.copy()
        for p in st.session_state.points:
            cv2.circle(display_img_array, p, brush_size, (108, 92, 231), -1)
        
        display_pil = Image.fromarray(display_img_array)
        
        st.write("Click the watermark below to mark it for removal:")
        value = streamlit_image_coordinates(display_pil, key="main_editor")
        
        if value:
            new_point = (value['x'], value['y'])
            if new_point not in st.session_state.points:
                st.session_state.points.append(new_point)
                st.rerun() # Refresh to show the new circle immediately

else:
    # Reset everything if no file is uploaded
    st.session_state.points = []
    st.session_state.result_img = None
    st.markdown("<div style='text-align: center; margin-top: 50px; color: #bbb;'>Upload a JPG or PNG to see the AI magic.</div>", unsafe_allow_html=True)
