import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(page_title="Pro Watermark Remover", layout="wide")

st.title("🖌️ Multi-Point Watermark Remover")
st.write("Click along the watermark to cover it entirely. Each click adds a 'healing' spot.")

# Initialize a 'memory' for your clicks so they don't disappear
if 'points' not in st.session_state:
    st.session_state.points = []

uploaded_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(img)
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Click to cover the watermark")
        # Record clicks on the image
        value = streamlit_image_coordinates(img, key="multiclick")
        
        if value:
            # Save the new click to our list
            point = (value['x'], value['y'])
            if point not in st.session_state.points:
                st.session_state.points.append(point)

        if st.button("Reset Clicks"):
            st.session_state.points = []
            st.rerun()

    with col2:
        st.subheader("2. Result")
        
        # Create a mask using ALL the points clicked
        mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
        brush_size = st.slider("Brush Size (Circle thickness)", 5, 100, 25)
        
        for p in st.session_state.points:
            cv2.circle(mask, p, brush_size, 255, -1)

        if st.button("Clean All Marked Spots"):
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            # Apply healing to the whole mask
            res_bgr = cv2.inpaint(img_bgr, mask, 10, cv2.INPAINT_TELEA)
            res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
            res_pil = Image.fromarray(res_rgb)
            
            st.image(res_pil, caption="Watermark Removed!")
            
            # Download
            buf = io.BytesIO()
            res_pil.save(buf, format="PNG")
            st.download_button("Download Image", buf.getvalue(), "cleaned.png")
        else:
            # Show a preview of the mask so you know where you've clicked
            preview_img = img_array.copy()
            for p in st.session_state.points:
                cv2.circle(preview_img, p, brush_size, (255, 0, 0), -1)
            st.image(preview_img, caption="Preview of areas to be cleaned")

else:
    st.session_state.points = []
    st.info("Upload an image to begin.")
