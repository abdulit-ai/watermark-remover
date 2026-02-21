import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Instant Watermark Remover", layout="centered")

st.title("📸 Instant Watermark Remover")
st.write("Upload your image and adjust the slider until the watermark disappears.")

uploaded_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Load image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    st.image(img_rgb, caption="Original Image", use_container_width=True)

    # Threshold slider - this helps find the watermark
    # If the watermark is white/bright, keep it high (200+). 
    # If it's darker, move it lower.
    sensitivity = st.slider("Detection Sensitivity (Adjust if watermark stays visible)", 50, 255, 220)

    if st.button("Remove Watermark Now"):
        # 1. Convert to grayscale to find text
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Create a mask of the bright parts (the watermark)
        _, mask = cv2.threshold(gray, sensitivity, 255, cv2.THRESH_BINARY)
        
        # 3. Slightly thicken the mask to cover edges
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        
        # 4. Use Telea Inpainting to heal the area
        result_bgr = cv2.inpaint(img, mask, 10, cv2.INPAINT_TELEA)
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        st.subheader("Result")
        st.image(result_rgb, use_container_width=True)
        
        # Download Button
        result_pil = Image.fromarray(result_rgb)
        buf = io.BytesIO()
        result_pil.save(buf, format="PNG")
        st.download_button("Download Cleaned Image", buf.getvalue(), "cleaned.png", "image/png")
else:
    st.info("Please upload an image in the sidebar to start.")
