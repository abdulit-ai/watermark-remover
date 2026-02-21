import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io

st.set_page_config(page_title="Watermark Remover", layout="wide")
st.title("🖌️ AI Watermark Remover")

uploaded_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Load original image
    original_pil = Image.open(uploaded_file).convert("RGB")
    width, height = original_pil.size
    
    # Scale for display
    canvas_width = 700
    ratio = canvas_width / width
    canvas_height = int(height * ratio)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Paint the Watermark")
        stroke_width = st.slider("Brush Size", 1, 50, 20)
        
        # We create a container to stack the canvas on top of a normal image
        # This prevents the 'image_to_url' error because we DON'T pass background_image
        st.image(original_pil, width=canvas_width)
        
        # The canvas is now just a blank transparent layer on top
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=stroke_width,
            stroke_color="#FF0000",
            update_streamlit=True,
            height=canvas_height,
            width=canvas_width,
            drawing_mode="freedraw",
            key="canvas",
            background_color="#00000000", # Fully transparent
        )
        st.caption("Tip: Draw on the box above to match the watermark position in the photo.")

    with col2:
        st.subheader("2. Result")
        if st.button("Clean Area"):
            if canvas_result.image_data is not None:
                # 1. Get the mask from the canvas drawing
                mask = canvas_result.image_data[:, :, 3] 
                mask = cv2.resize(mask, (width, height))
                
                # 2. Process
                img_array = np.array(original_pil)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # 3. Heal (Inpaint)
                res_bgr = cv2.inpaint(img_bgr, mask, 3, cv2.INPAINT_TELEA)
                res_rgb = cv2.cvtColor(res_bgr, cv2.COLOR_BGR2RGB)
                res_pil = Image.fromarray(res_rgb)
                
                st.image(res_pil, use_container_width=True)
                
                # 4. Download
                buf = io.BytesIO()
                res_pil.save(buf, format="PNG")
                st.download_button("Download Image", buf.getvalue(), "cleaned.png", "image/png")
else:
    st.info("Please upload an image in the sidebar.")
