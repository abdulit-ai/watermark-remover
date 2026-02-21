import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st

# 1. Page Config
st.set_page_config(page_title="EzRemove", layout="wide")

# 2. Modern SaaS CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #1e293b; }
    [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderSize"], 
    [data-testid="stFileUploaderDeleteBtn"], .uploadedFile { display: none !important; }
    .stButton>button { 
        background-color: #4f46e5; color: white !important; 
        border-radius: 12px; width: 100%; font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("EzRemove AI")
st.write("Upload an image and use the slider to highlight the watermark.")

# 3. App Logic
file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if file:
    # Load Image
    img = Image.open(file).convert("RGB")
    img_array = np.array(img)
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("Controls")
        # This slider finds bright pixels (like text/logos)
        sensitivity = st.slider("Watermark Detection Sensitivity", 50, 255, 200)
        st.info("Adjust the slider until the watermark looks white in the preview below.")
        
        # Create mask based on brightness
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        _, mask = cv2.threshold(gray, sensitivity, 255, cv2.THRESH_BINARY)
        
        # Thicken the mask slightly to cover edges
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        
        st.image(mask, caption="AI Detection Mask (White = area to remove)", width=250)
        
        if st.button("✨ Clean Image Now"):
            # Process
            bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            res_bgr = cv2.inpaint(bgr, mask, 3, cv2.INPAINT_TELEA)
            res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
            res_pil = Image.fromarray(res_rgb)
            
            st.session_state.final = res_pil
            st.rerun()

    with col2:
        if 'final' in st.session_state:
            st.image(st.session_state.final, use_container_width=True, caption="Restored Image")
            
            buf = io.BytesIO()
            st.session_state.final.save(buf, format="PNG")
            st.download_button("Download Result", buf.getvalue(), "cleaned.png")
            
            if st.button("Start New Project"):
                del st.session_state.final
                st.rerun()
        else:
            st.image(img, use_container_width=True, caption="Original Image")
else:
    if 'final' in st.session_state:
        del st.session_state.final
