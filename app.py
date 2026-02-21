import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.title("📸 Smart Watermark Remover")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 1. Load Image and fix Colors
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Fix the blue tint!

    st.image(img_rgb, caption="Original Image")

    # 2. Add a slider to help find the watermark
    sensitivity = st.slider("Watermark Detection Sensitivity", 0, 255, 200)

    if st.button("Clean Image"):
        # Convert to grayscale to find the text/logo
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Create a 'mask' of the watermark
        _, mask = cv2.threshold(gray, sensitivity, 255, cv2.THRESH_BINARY)
        
        # Dilate the mask (make the 'search area' slightly bigger for better blending)
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)

        # Inpaint: This 'heals' the area under the mask
        result_bgr = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)

        st.image(result_rgb, caption="Result")

        # Download Button
        res_pil = Image.fromarray(result_rgb)
        st.download_button("Download Cleaned Image", data=uploaded_file, file_name="cleaned.png")
