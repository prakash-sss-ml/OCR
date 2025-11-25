import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.set_page_config(page_title="PDF OCR (Auto Rotate)", layout="centered")
st.title("📄 PDF OCR with Auto-Rotation (Tesseract)")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])


def pdf_to_images(pdf_bytes):
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in pdf:
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)
    return images


def auto_rotate(image):
    """Detect rotation using Tesseract OSD and rotate image correctly"""
    osd = pytesseract.image_to_osd(image)
    rotation_angle = int(osd.split("Rotate:")[1].split("\n")[0].strip())
    corrected_img = image.rotate(-rotation_angle, expand=True)
    return corrected_img, rotation_angle


if st.button("Extract Text"):
    if uploaded_file is None:
        st.error("⚠️ Please upload a PDF first.")
    else:
        st.info("⏳ Processing PDF...")

        images = pdf_to_images(uploaded_file.read())
        extracted_text = ""

        for idx, img in enumerate(images):
            st.write(f"### 📄 Page {idx+1} Preview (Original)")
            st.image(img, use_column_width=True)

            # Auto-rotation
            rotated_img, angle = auto_rotate(img)

            st.write(f"🔄 Detected rotation: **{angle}°** → Corrected")
            st.image(rotated_img, use_column_width=True)

            # OCR
            text = pytesseract.image_to_string(rotated_img)

            extracted_text += f"\n\n===== PAGE {idx+1} =====\n{text}"

        st.subheader("📝 Corrected Text Output")
        st.text(extracted_text)
