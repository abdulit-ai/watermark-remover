import io
import numpy as np
from PIL import Image
import streamlit as st
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates

# 1. Page Config
st.set_page_config(page_title="EzRemove | Pro Watermark Eraser", layout="wide")

# 2. Premium SaaS CSS (AirBrush / HitPaw Style)
st.markdown("""
    <style>
    /* Clean SaaS Background */
    .stApp { background-color: #f9fafb; color: #111827; }
    
    /* Hide Streamlit Clutter */
    [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderSize"], 
    [data-testid="stFileUploaderDeleteBtn"], .uploadedFile { display: none !important; }
    section[data-testid="stSidebar"] { display: none; }

    /* Modern Navbar */
    .nav-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 15px 50px; background: white; border-bottom: 1px solid #e5e7eb;
        position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
    }
    .logo-text { font-size: 24px; font-weight: 800; color: #4f46e5; letter-spacing: -1px; }

    /* Hero Section (Upload Page) */
    .hero-container {
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; height: 80vh; padding-top: 100px;
    }
    .upload-card {
        background: white; padding: 60px; border-radius: 24px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border: 2px dashed #e5e7eb; width: 100%; max-width: 600px; text-align: center;
    }
    
    /* Editor Style */
    .editor-container { padding-top: 100px; max-width: 1200px; margin: auto; }
    .stButton>button {
        background: #4f46e5; color: white !important; border-radius: 12px;
        border: none; padding: 12px 24px; font-weight: 600; width: 100%; transition: 0.2s;
    }
    .stButton>button:hover { background: #4338ca; transform: translateY(-1px); }
    
    /* Custom Slider */
    .stSlider { padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Navbar
st.markdown("""
    <div class="nav-bar">
        <div class="logo-text">EzRemove.ai</div>
        <div style="font-size: 14px; font-weight: 600; color: #6b7280;">
            Tools &nbsp;&nbsp;&nbsp; Pricing &nbsp;&nbsp;&nbsp; 
            <span style="background: #111827; color: white; padding: 10px 22px; border-radius: 10px;">Login</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 4. State Management
if 'img_data' not in st.session_state:
    st.session_state.img_data = None
if 'points' not in st.session_state:
    st.session_state.points = []
if 'result' not in st.session_state:
    st.session_state.result = None

# 5. Routing Logic
if st.session_state.img_data is None:
    # LANDING PAGE / UPLOAD
    st.markdown("""
        <div class="hero-container">
            <h1 style="font-size: 56px; font-weight: 900; margin-bottom: 10px;">Remove watermarks <span style="color: #4f46e5;">instantly.</span></h1>
            <p style="font-size: 18px; color: #6b7280; margin-bottom: 40px;">AI-powered object removal for clean, professional photos.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Centered Upload Box
    cols = st.columns([1, 2, 1])
    with cols[1]:
        uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], key="home_uploader")
        if uploaded_file:
            st.session_state.img_data = uploaded_file
            st.rerun()
else:
    # EDITOR PAGE
    st.markdown('<div class="editor-container">', unsafe_allow_html=True)
    
    img_pil = Image.open(st.session_state.img_data).convert("RGB")
    img_array = np.array(img_pil)
    
    # Work Tool Row
    tool_col1, tool_col2, tool_col3, tool_col4 = st.columns([2, 1, 1, 1])
    
    with tool_col1:
        brush = st.select_slider("Brush Size", options=[10, 20, 30, 50, 80], value=30)
    with tool_col2:
        st.write("") # Spacer
        if st.button("✨ Remove Now"):
            if st.session_state.points:
                mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
                for p in st.session_state.points:
                    cv2.circle(mask, p, brush, 255, -1)
                
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                res_bgr = cv2.inpaint(img_bgr, mask, 3, cv2.INPAINT_TELEA)
                st.session_state.result = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                st.session_state.points = [] # Clear after processing
                st.rerun()
    with tool_col3:
        st.write("") # Spacer
        if st.button("🔄 Reset"):
            st.session_state.points = []
            st.session_state.result = None
            st.rerun()
    with tool_col4:
        st.write("") # Spacer
        if st.button("🏠 Exit"):
            st.session_state.img_data = None
            st.session_state.points = []
            st.session_state.result = None
            st.rerun()

    # Workspace
    st.divider()
    
    if st.session_state.result is not None:
        res_pil = Image.fromarray(st.session_state.result)
        st.image(res_pil, use_container_width=True)
        
        buf = io.BytesIO()
        res_pil.save(buf, format="PNG")
        st.download_button("⬇️ Download High-Res", buf.getvalue(), "cleaned.png")
    else:
        # Show image with active selection markers
        display_img = img_array.copy()
        for p in st.session_state.points:
            cv2.circle(display_img, p, brush, (79, 70, 229), -1)
        
        # Unified coordinate tool
        out = streamlit_image_coordinates(Image.fromarray(display_img), key="pro_editor")
        if out:
            st.session_state.points.append((out['x'], out['y']))
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
