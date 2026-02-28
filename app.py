import io
import numpy as np
from PIL import Image
import streamlit as st
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(page_title="Pro Watermark Remover", layout="wide")

st.title("🖌️ Multi-Point Watermark Remover")

if 'points' not in st.session_state:
    st.session_state.points = []

uploaded_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(img)
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Click the watermark")
        value = streamlit_image_coordinates(img, key="multiclick")
        
        if value:
            point = (value['x'], value['y'])
            if point not in st.session_state.points:
                st.session_state.points.append(point)

        if st.button("Reset Clicks"):
            st.session_state.points = []
            st.rerun()

    with col2:
        st.subheader("2. Result")
        mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
        brush_size = st.slider("Brush Size", 5, 100, 25)
        
        for p in st.session_state.points:
            cv2.circle(mask, p, brush_size, 255, -1)

        if st.button("Clean All Marked Spots"):
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            res_bgr = cv2.inpaint(img_bgr, mask, 10, cv2.INPAINT_TELEA)
            res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
            res_pil = Image.fromarray(res_rgb)
            st.image(res_pil)
            
            buf = io.BytesIO()
            res_pil.save(buf, format="PNG")
            st.download_button("Download Image", buf.getvalue(), "cleaned.png")
        else:
            preview_img = img_array.copy()
            for p in st.session_state.points:
                cv2.circle(preview_img, p, brush_size, (255, 0, 0), -1)
            st.image(preview_img)
else:
    st.info("Upload an image in the sidebar.")
