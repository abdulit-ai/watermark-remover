import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

# 1. Page Config - Forced Light Theme for Visibility
st.set_page_config(page_title="EzRemove", layout="wide")

# 2. Simple, High-Visibility CSS
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p { color: #1e293b !important; font-family: sans-serif; }
    .stButton>button { 
        background-color: #4f46e5; 
        color: white !important; 
        border-radius: 8px; 
        padding: 10px;
        font-weight: bold;
    }
    div[data-testid="stFileUploader"] { 
        border: 2px solid #e2e8f0; 
        border-radius: 12px; 
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("EzRemove AI")
st.write("Upload an image and click the watermark to erase it.")

# 3. State Management
if 'points' not in st.session_state:
    st.session_state.points = []
if 'result' not in st.session_state:
    st.session_state.result = None

# 4. Main Workflow
uploaded_file = st.file_uploader("Choose a photo", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Use a simpler loading method
    raw_img = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(raw_img)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Controls")
        brush_size = st.slider("Brush Size", 10, 100, 30)
        
        if st.button("✨ ERASE WATERMARK"):
            if st.session_state.points:
                # Create mask
                mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
                for p in st.session_state.points:
                    cv2.circle(mask, p, brush_size, 255, -1)
                
                # Inpaint
                bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                res_bgr = cv2.inpaint(bgr, mask, 3, cv2.INPAINT_TELEA)
                st.session_state.result = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                st.session_state.points = [] # Reset points
                st.rerun()
        
        if st.button("🔄 RESET ALL"):
            st.session_state.points = []
            st.session_state.result = None
            st.rerun()

    with col2:
        if st.session_state.result is not None:
            st.image(st.session_state.result, use_container_width=True, caption="Cleaned Image")
            
            # Download Button
            res_pil = Image.fromarray(st.session_state.result)
            buf = io.BytesIO()
            res_pil.save(buf, format="PNG")
            st.download_button("Download Result", buf.getvalue(), "cleaned.png")
        else:
            # DRAWING MARKERS
            display_img = img_array.copy()
            for p in st.session_state.points:
                cv2.circle(display_img, p, brush_size, (79, 70, 229), -1)
            
            st.write("Click precisely on the watermark:")
            # Use the most basic display parameters
            value = streamlit_image_coordinates(Image.fromarray(display_img), key="editor")
            
            if value:
                st.session_state.points.append((value['x'], value['y']))
                st.rerun()

else:
    st.session_state.points = []
    st.session_state.result = None
