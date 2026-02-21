import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

st.title("🖌️ Pro Watermark Remover")
st.write("Draw over the watermark with the brush, then click 'Clean'")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png"])

if uploaded_file:
    bg_image = Image.open(uploaded_file)
    width, height = bg_image.size
    
    # Scale for display if too large
    display_width = 700
    ratio = display_width / width
    display_height = int(height * ratio)

    st.subheader("Step 1: Paint over the watermark")
    stroke_width = st.slider("Brush size:", 1, 50, 15)
    
    # Create a canvas for the user to draw on
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color="#FFFFFF",
        background_image=bg_image,
        update_streamlit=True,
        height=display_height,
        width=display_width,
        drawing_mode="freedraw",
        key="canvas",
    )

    if st.button("Clean Selected Area"):
        if canvas_result.image_data is not None:
            # 1. Get the mask from the canvas
            mask = canvas_result.image_data[:, :, 3] # Get the 'alpha' layer (where you drew)
            mask = cv2.resize(mask, (width, height)) # Scale back to original size
            
            # 2. Convert original image for OpenCV
            img = np.array(bg_image.convert("RGB"))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # 3. Heal the image
            # We use a larger radius (7) to blend complex AI watermarks better
            result_bgr = cv2.inpaint(img, mask, 7, cv2.INPAINT_NS)
            result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
            
            st.subheader("Step 2: Result")
            st.image(result_rgb)
            
            # Download
            res_pil = Image.fromarray(result_rgb)
            st.download_button("Download Cleaned Image", data=uploaded_file, file_name="cleaned.png")
