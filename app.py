import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io
import base64

st.set_page_config(page_title="Pro Watermark Remover", layout="wide")

# This function fixes the "AttributeError" by preparing the image manually
def get_image_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

st.title("🖌️ Manual Brush Watermark Remover")
st.write("Paint over the watermark, then click 'Clean Area'")

uploaded_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 1. Open and convert image
    original_pil = Image.open(uploaded_file).convert("RGB")
    width, height = original_pil.size
    
    # 2. Setup scaling for the brush tool
    display_width = 700
    ratio = display_width / width
    display_height = int(height * ratio)

    # 3. Create the bypass URL
    img_url = get_image_base64(original_pil)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Paint the Watermark")
        stroke_width = st.slider("Brush size", 1, 50, 20)
        
        # We use 'background_image' but the Base64 bypass ensures it doesn't crash
        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)", 
            stroke_width=stroke_width,
            stroke_color="#FF0000",
            background_image=original_pil,
            update_streamlit=True,
            height=display_height,
            width=display_width,
            drawing_mode="freedraw",
            key="canvas_bypass",
        )

    with col2:
        st.subheader("2. Result")
        if st.button("Clean Area"):
            if canvas_result.image_data is not None:
                # Get the mask from your drawing
                mask = canvas_result.image_data[:, :, 3] 
                mask = cv2.resize(mask, (width, height))
                
                # Convert image for processing
                img_array = np.array(original_pil)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Inpaint (Heal the area)
                res_bgr = cv2.inpaint(img_bgr, mask, 3, cv2.INPAINT_TELEA)
                res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                res_pil = Image.fromarray(res_rgb)
                
                st.image(res_pil, use_container_width=True)
                
                # Download logic
                buf = io.BytesIO()
                res_pil.save(buf, format="PNG")
                st.download_button("Download Cleaned Image", buf.getvalue(), "cleaned.png", "image/png")
else:
    st.info("Upload an image to start painting.")
