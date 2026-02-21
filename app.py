import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io
import base64

# Set page to wide mode
st.set_page_config(page_title="AI Watermark Remover", layout="wide")

st.title("🖌️ AI Watermark Remover")
st.write("1. Upload image | 2. Paint over the watermark | 3. Click 'Clean'")

uploaded_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

def get_image_base64(img):
    """Helper to convert image to a format the canvas won't crash on"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

if uploaded_file:
    # Load and prepare image
    original_pil = Image.open(uploaded_file).convert("RGB")
    width, height = original_pil.size
    
    # Scale image to fit the screen
    display_width = 700
    ratio = display_width / width
    display_height = int(height * ratio)

    # WORKAROUND: Convert to Base64 to avoid AttributeError
    bg_url = get_image_base64(original_pil)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Step 1: Paint the watermark")
        stroke_width = st.slider("Brush Size", 1, 50, 15)
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)", 
            stroke_width=stroke_width,
            stroke_color="#FFFFFF",
            background_image=original_pil,
            background_label=bg_url, # Adding this help the library find the URL
            update_streamlit=True,
            height=display_height,
            width=display_width,
            drawing_mode="freedraw",
            key="canvas",
        )

    with col2:
        st.subheader("Step 2: Results")
        if st.button("Clean Selected Area"):
            if canvas_result.image_data is not None:
                # 1. Create a mask from drawing
                mask = canvas_result.image_data[:, :, 3] 
                mask = cv2.resize(mask, (width, height))
                
                # 2. Convert to OpenCV format
                img_bgr = cv2.cvtColor(np.array(original_pil), cv2.COLOR_RGB2BGR)
                
                # 3. Apply Inpaint
                result_bgr = cv2.inpaint(img_bgr, mask, 7, cv2.INPAINT_NS)
                
                # 4. Convert back to RGB
                result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
                result_pil = Image.fromarray(result_rgb)
                
                st.image(result_pil, caption="Watermark Removed!")
                
                # 5. Prepare download button
                buf = io.BytesIO()
                result_pil.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="Download Clean Image",
                    data=byte_im,
                    file_name="cleaned_image.png",
                    mime="image/png"
                )
        else:
            st.info("Paint over the watermark on the left, then click 'Clean'")
else:
    st.info("Please upload an image in the sidebar to begin.")
