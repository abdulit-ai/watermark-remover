import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_canvas_events import st_canvas
import io

st.set_page_config(page_title="Pro Watermark Remover", layout="wide")

st.title("🖌️ Long Watermark Remover")
st.write("Scribble/Click along the entire watermark, then click 'Clean'")

uploaded_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Load image
    img_pil = Image.open(uploaded_file).convert("RGB")
    width, height = img_pil.size
    
    # Scale for display
    display_width = 800
    ratio = display_width / width
    display_height = int(height * ratio)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Trace the watermark")
        # The new stable canvas tool
        points = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=20,
            stroke_color="#FF0000",
            background_image=img_pil,
            width=display_width,
            height=display_height,
            drawing_mode="freedraw",
            key="canvas",
        )

    with col2:
        st.subheader("2. Result")
        if st.button("Clean Entire Trace"):
            if points.image_data is not None:
                # 1. Get the drawing mask
                # This captures your entire long scribble
                mask = points.image_data[:, :, 3] 
                mask = cv2.resize(mask, (width, height))
                
                # 2. Convert for OpenCV
                img_array = np.array(img_pil)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # 3. Heal the image along the scribble
                # We use a slightly higher radius (10) to blend long lines better
                res_bgr = cv2.inpaint(img_bgr, mask, 10, cv2.INPAINT_TELEA)
                res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                res_pil = Image.fromarray(res_rgb)
                
                st.image(res_pil, use_container_width=True)
                
                # 4. Download
                buf = io.BytesIO()
                res_pil.save(buf, format="PNG")
                st.download_button("Download Cleaned Image", buf.getvalue(), "cleaned.png")
else:
    st.info("Please upload an image in the sidebar.")
