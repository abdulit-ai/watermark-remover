import io
import numpy as np
from PIL import Image
import streamlit as st
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates

# 1. Page Configuration
st.set_page_config(page_title="ClearLens | Image Restoration", layout="wide")

# 2. Custom Modern CSS
st.markdown("""
    <style>
    /* Main background and font */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Header styling */
    h1 {
        color: #1a1c23;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e9ecef;
    }
    
    /* Clean Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: none;
        background-color: #2d3436;
        color: white;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #000000;
        border: none;
        color: white;
    }
    
    /* Image Preview Container */
    .img-container {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Setup
with st.sidebar:
    st.title("ClearLens")
    st.write("Professional object and watermark removal tool.")
    st.divider()
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        st.divider()
        brush_size = st.slider("Selection Precision", 5, 100, 25)
        if st.button("Reset Selection"):
            st.session_state.points = []
            st.rerun()

# 4. Main Logic
if 'points' not in st.session_state:
    st.session_state.points = []

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(img)
    
    st.title("Image Editor")
    
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 1. Select Target Area")
        st.caption("Click the watermark or object you wish to remove.")
        # Modern click interface
        value = streamlit_image_coordinates(img, key="multiclick")
        
        if value:
            point = (value['x'], value['y'])
            if point not in st.session_state.points:
                st.session_state.points.append(point)

    with col2:
        st.markdown("### 2. Processing & Export")
        
        mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
        for p in st.session_state.points:
            cv2.circle(mask, p, brush_size, 255, -1)

        if st.button("Generate Clean Image"):
            with st.spinner("Processing AI Restoration..."):
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                res_bgr = cv2.inpaint(img_bgr, mask, 10, cv2.INPAINT_TELEA)
                res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                res_pil = Image.fromarray(res_rgb)
                
                st.image(res_pil, use_container_width=True)
                
                # Download
                buf = io.BytesIO()
                res_pil.save(buf, format="PNG")
                st.download_button(
                    label="Download Final Image",
                    data=buf.getvalue(),
                    file_name="clearlens_export.png",
                    mime="image/png"
                )
        else:
            if st.session_state.points:
                preview_img = img_array.copy()
                for p in st.session_state.points:
                    cv2.circle(preview_img, p, brush_size, (255, 0, 0), -1)
                st.image(preview_img, use_container_width=True)
            else:
                st.info("Awaiting selection. Please click on the original image to begin.")
else:
    st.session_state.points = []
    st.header("Welcome to ClearLens")
    st.write("Select an image from the sidebar to start your restoration project.")
