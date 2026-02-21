import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="Watermark Remover", layout="centered")

st.title("📸 Simple Watermark Remover")
st.write("Upload an image and use the tool to clean it up.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Convert file to OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    st.image(image, channels="BGR", caption="Original Image")

    if st.button("Remove Watermark"):
        # Note: True automated removal often requires a mask. 
        # Here we use a simple 'Inpaint' method as a baseline.
        # For a production app, you'd integrate an AI model like 'Lama'.
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Inpaint to fill the watermark area
        dst = cv2.inpaint(image, thresh, 3, cv2.INPAINT_TELEA)
        
        st.image(dst, channels="BGR", caption="Processed Image")
        
        # Download button
        _, buffer = cv2.imencode('.png', dst)
        st.download_button(
            label="Download Clean Image",
            data=buffer.tobytes(),
            file_name="cleaned_image.png",
            mime="image/png"
        )
