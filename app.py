import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

# 1. Page Setup
st.set_page_config(page_title="EzRemove", layout="wide")

# 2. Modern SaaS CSS (Forces file info to disappear)
st.markdown("""
    <style>
    /* Clean Light SaaS Background */
    .stApp { background-color: #f3f4f6; color: #111827; }
    
    /* HIDE THE FILE UPLOADER INFO (The part you don't like) */
    [data-testid="stFileUploaderFileName"], 
    [data-testid="stFileUploaderSize"], 
    [data-testid="stFileUploaderDeleteBtn"],
    .uploadedFile { display: none !important; }

    /* Custom Buttons */
    .stButton>button {
        background: #4f46e5; color: white !important; border-radius: 12px;
        border: none; padding: 12px; font-weight: 600; width: 100%;
    }
    
    /* Box around the editor */
    .editor-card {
        background: white; padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. State Management
if 'points' not in st.session_state:
    st.session_state.points = []
if 'result' not in st.session_state:
    st.session_state.result = None

# Header
st.markdown("<h1 style='color: #4f46e5;'>EzRemove AI</h1>", unsafe_allow_html=True)

# 4. Upload Section
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    # Load Image
    img_pil = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(img_pil)
    
    col1, col2 = st.columns([1, 4], gap="large")
    
    with col1:
        st.write("### Controls")
        brush_size = st.slider("Brush Size", 10, 100, 30)
        
        if st.button("✨ Erase"):
            if st.session_state.points:
                mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
                for p in st.session_state.points:
                    cv2.circle(mask, p, brush_size, 255, -1)
                
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                res_bgr = cv2.inpaint(img_bgr, mask, 3, cv2.INPAINT_TELEA)
                st.session_state.result = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                st.session_state.points = [] 
                st.rerun()
        
        if st.button("🔄 Reset"):
            st.session_state.points = []
            st.session_state.result = None
            st.rerun()

    with col2:
        # Check if we should show the cleaned result or the original
        if st.session_state.result is not None:
            st.image(st.session_state.result, use_container_width=True)
            
            # Download
            res_pil = Image.fromarray(st.session_state.result)
            buf = io.BytesIO()
            res_pil.save(buf, format="PNG")
            st.download_button("Download Cleaned Image", buf.getvalue(), "cleaned.png")
        else:
            # FORCE RENDER: Create the display image with selection dots
            display_img = img_array.copy()
            for p in st.session_state.points:
                cv2.circle(display_img, p, brush_size, (79, 70, 229), -1)
            
            # This is the interactive image. It should show now!
            st.write("Click on the watermark to mark it:")
            value = streamlit_image_coordinates(Image.fromarray(display_img), key="editor_v5")
            
            if value:
                st.session_state.points.append((value['x'], value['y']))
                st.rerun()
else:
    st.session_state.points = []
    st.session_state.result = None
    st.markdown("<div style='text-align: center; margin-top: 100px; color: #9ca3af;'><h2>Drop an image here</h2></div>", unsafe_allow_html=True)
