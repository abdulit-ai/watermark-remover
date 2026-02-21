import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Watermark Remover", layout="wide")

st.title("🖌️ Permanent Fix: Watermark Remover")
st.write("Select the watermark area on the image, then click 'Clean Area'")

uploaded_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 1. Load Image
    img = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(img)
    
    st.subheader("Step 1: Select the Watermark")
    st.write("Click and drag over the watermark in the image below:")
    
    # This is the stable, built-in way to select areas in Streamlit 2026
    # It replaces the broken 'st_canvas'
    from streamlit_image_coordinates import streamlit_image_coordinates
    
    # We show the image and get the click coordinates
    conf = streamlit_image_coordinates(img, key="pilot")

    if conf:
        st.write(f"Area Selected at: {conf['x']}, {conf['y']}")
        
        if st.button("Clean This Area"):
            # Create a circular mask where you clicked
            mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
            cv2.circle(mask, (conf['x'], conf['y']), 30, 255, -1) # 30 is brush size
            
            # 2. Process with OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            res_bgr = cv2.inpaint(img_bgr, mask, 10, cv2.INPAINT_TELEA)
            res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
            res_pil = Image.fromarray(res_rgb)
            
            st.subheader("Step 2: Result")
            st.image(res_pil)
            
            # 3. Download
            buf = io.BytesIO()
            res_pil.save(buf, format="PNG")
            st.download_button("Download Image", buf.getvalue(), "cleaned.png")
    else:
        st.info("Click directly on the watermark in the image above.")

else:
    st.info("Please upload an image in the sidebar.")
