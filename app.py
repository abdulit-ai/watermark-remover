import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_cropper import st_cropper

# 1. Page Config
st.set_page_config(page_title="EzRemove Pro", layout="wide")

# 2. SaaS Styling
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #1e293b; }
    [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderSize"], 
    [data-testid="stFileUploaderDeleteBtn"], .uploadedFile { display: none !important; }
    .stButton>button { 
        background-color: #4f46e5; color: white !important; 
        border-radius: 12px; width: 100%; font-weight: 600; height: 50px;
    }
    .instruction-card {
        background: white; padding: 20px; border-radius: 15px;
        border: 1px solid #e2e8f0; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("EzRemove AI")

# 3. File Upload
file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if file:
    img = Image.open(file).convert("RGB")
    img_array = np.array(img)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="instruction-card"><b>Manual Selection:</b> Drag the box over the watermark you want to remove.</div>', unsafe_allow_html=True)
        
        # This is our manual "Box" selector. It is much more stable than clicking.
        rect = st_cropper(img, realtime_update=True, box_color='#4f46e5', aspect_ratio=None)
        
        # Get coordinates of the box
        # We access the internal box coordinates provided by the cropper
        box = rect.getbbox() # [left, top, right, bottom]
        
    with col2:
        st.subheader("Result")
        if st.button("✨ Remove Watermark in Box"):
            with st.spinner("AI Healing..."):
                # Create a mask based on the box coordinates
                mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
                
                # We draw a white rectangle on the mask where the box was
                left, top, right, bottom = box
                # Scale coordinates if necessary (though cropper handles this well)
                cv2.rectangle(mask, (int(left), int(top)), (int(right), int(bottom)), 255, -1)
                
                # Apply Inpainting
                bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                res_bgr = cv2.inpaint(bgr, mask, 7, cv2.INPAINT_TELEA)
                res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                res_pil = Image.fromarray(res_rgb)
                
                st.image(res_pil, use_container_width=True, caption="Cleaned Image")
                
                # Download
                buf = io.BytesIO()
                res_pil.save(buf, format="PNG")
                st.download_button("Download Result", buf.getvalue(), "cleaned.png")
        else:
            st.info("Position the box on the left, then click the button above.")

else:
    st.markdown("<div style='text-align: center; margin-top: 100px; color: #94a3b8;'><h2>Drop your image here to start</h2></div>", unsafe_allow_html=True)
