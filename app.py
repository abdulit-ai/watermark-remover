import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io

# Basic config
st.set_page_config(page_title="Watermark Remover", layout="wide")

st.title("🖌️ Watermark Remover")

# Sidebar for upload
uploaded_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Open image and convert to RGB
    img = Image.open(uploaded_file).convert("RGB")
    
    # Scale for canvas display
    width, height = img.size
    display_width = 700
    ratio = display_width / width
    display_height = int(height * ratio)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Paint over watermark")
        stroke_width = st.slider("Brush Size", 1, 50, 15)
        
        # In Streamlit 1.24.0, passing the PIL image directly is stable
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=stroke_width,
            stroke_color="#FFFFFF",
            background_image=img,
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
                # 1. Extract mask from drawing (Alpha channel)
                mask = canvas_result.image_data[:, :, 3]
                mask = cv2.resize(mask, (width, height))
                
                # 2. Prepare image for OpenCV
                img_array = np.array(img)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # 3. Heal the image (Inpaint)
                # Increase radius to 10 for better blending of thick watermarks
                res_bgr = cv2.inpaint(img_bgr, mask, 10, cv2.INPAINT_TELEA)
                
                # 4. Convert back to displayable format
                res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                res_pil = Image.fromarray(res_rgb)
                
                st.image(res_pil, caption="Processed Image")
                
                # 5. Download setup
                buf = io.BytesIO()
                res_pil.save(buf, format="PNG")
                st.download_button(
                    label="Download Image",
                    data=buf.getvalue(),
                    file_name="cleaned.png",
                    mime="image/png"
                )
        else:
            st.info("Use your mouse to paint the watermark on the left, then click 'Clean Area'")
else:
    st.info("Waiting for image upload...")
