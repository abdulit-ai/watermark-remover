import io
import numpy as np
from PIL import Image
import streamlit as st
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates

# 1. Page Config
st.set_page_config(page_title="EzRemove | AI Watermark Remover", layout="centered")

# 2. Advanced Professional CSS
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Center the main container */
    .main-container {
        max-width: 800px;
        margin: auto;
        text-align: center;
    }

    /* Spiral Logo Animation Effect */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .spiral-logo {
        width: 60px;
        height: 60px;
        border: 6px solid #4834d4;
        border-top: 6px solid #686de0;
        border-radius: 50%;
        margin-right: 15px;
    }

    /* Navigation Bar Simulation */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 0;
        border-bottom: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 40px;
    }

    /* Upload Box - Glassmorphism */
    div[data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 2px dashed #4834d4;
        padding: 40px !important;
        transition: 0.3s;
    }

    /* Custom Buttons */
    .stButton>button {
        background: linear-gradient(to right, #4834d4, #686de0);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 50px;
        font-weight: 600;
        width: 100%;
        box-shadow: 0 4px 15px rgba(72, 52, 212, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(72, 52, 212, 0.4);
        color: white;
    }

    /* Hide Sidebar and Streamlit branding */
    section[data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Header / Logo Section
st.markdown(f"""
    <div class="nav-bar">
        <div style="display: flex; align-items: center;">
            <div class="spiral-logo"></div>
            <h2 style="margin: 0; color: #1a1c23; font-size: 24px;">EzRemove</h2>
        </div>
        <div style="color: #636e72; font-weight: 500;">
            Log in &nbsp;&nbsp;&nbsp; 
            <span style="background: #1a1c23; color: white; padding: 8px 18px; border-radius: 20px;">Try Free</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 4. Main UI Logic
if 'points' not in st.session_state:
    st.session_state.points = []

st.markdown("<h1 style='text-align: center;'>AI Watermark Remover</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #636e72;'>Upload your image and click the watermark to erase it instantly.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(img)
    
    # Selection Area
    st.markdown("---")
    col_img, col_ctrl = st.columns([2, 1])

    with col_img:
        st.write("### Target Selection")
        # Center the coordinate tool
        value = streamlit_image_coordinates(img, key="multiclick")
        
        if value:
            point = (value['x'], value['y'])
            if point not in st.session_state.points:
                st.session_state.points.append(point)

    with col_ctrl:
        st.write("### Settings")
        brush_size = st.slider("Brush Thickness", 10, 150, 40)
        
        if st.button("✨ Clean Image"):
            with st.spinner("AI is analyzing pixels..."):
                mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
                for p in st.session_state.points:
                    cv2.circle(mask, p, brush_size, 255, -1)

                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                res_bgr = cv2.inpaint(img_bgr, mask, 10, cv2.INPAINT_TELEA)
                res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                res_pil = Image.fromarray(res_rgb)
                
                st.image(res_pil, use_container_width=True)
                
                buf = io.BytesIO()
                res_pil.save(buf, format="PNG")
                st.download_button("Download HD Result", buf.getvalue(), "ezremove_clean.png")

        if st.button("Reset All"):
            st.session_state.points = []
            st.rerun()

    # Preview Overlay
    if st.session_state.points:
        st.write("Selected areas:")
        preview_img = img_array.copy()
        for p in st.session_state.points:
            cv2.circle(preview_img, p, brush_size, (255, 0, 0), -1)
        st.image(preview_img, width=300)

else:
    st.session_state.points = []
    st.markdown("<br><br><p style='text-align: center; opacity: 0.5;'>Supports PNG, JPG, JPEG, WEBP</p>", unsafe_allow_html=True)
