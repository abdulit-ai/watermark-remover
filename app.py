import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io
import base64

st.set_page_config(page_title="Watermark Remover", layout="wide")

st.title("🖌️ AI Watermark Remover")

# Helper function to bypass the broken 'image_to_url' in the library
def get_canvas_image(pil_image):
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

uploaded_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 1. Load Image
    img = Image.open(uploaded_file).convert("RGB")
    width, height = img.size
    
    # 2. Scale for display
    display_width = 700
    ratio = display_width / width
    display_height = int(height * ratio)

    # 3. CONVERT TO BASE64 (The Secret Sauce)
    bg_data = get_canvas_image(img)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Paint over watermark")
        stroke_width = st.slider("Brush Size", 1, 50, 20)
        
        # We pass the Base64 string to 'background_image' instead of the PIL object
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=stroke_width,
            stroke_color="#FFFFFF",
            background_image=Image.open(io.BytesIO(base64.b64decode(bg_data.split(',')[1]))),
            update_streamlit=True,
            height=display_height,
            width=display_width,
            drawing_mode="freedraw",
            key="canvas",
        )

    with col2:
        st.subheader("2. Result")
        if st.button("Clean Area"):
            if canvas_result.image_data is not None:
                # Get the mask from the canvas
                mask = canvas_result.image_data[:, :, 3]
                mask = cv2.resize(mask, (width, height))
                
                # OpenCV Processing
                img_array = np.array(img)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Inpaint (Heal)
                res_bgr = cv2.inpaint(img_bgr, mask, 3, cv2.INPAINT_TELEA)
                res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                res_pil = Image.fromarray(res_rgb)
                
                st.image(res_pil)
                
                # Download
                buf = io.BytesIO()
                res_pil.save(buf, format="PNG")
                st.download_button("Download Image", buf.getvalue(), "cleaned.png", "image/png")
else:
    st.info("Please upload an image in the sidebar.")
