import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import json
from openai import OpenAI

from dotenv import load_dotenv
import os



# -----------------------------------------
# 🔑 OPENAI CLIENT
# -----------------------------------------

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================
# 🧠 Tesseract Path
# ============================================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ============================================
# ⚙️ Streamlit App
# ============================================
st.set_page_config(page_title="PCB RFQ Auto-Fill (GPT-4o)", layout="wide")
st.title("📄 PCB RFQ Auto-Fill using GPT-4o + OCR")

uploaded_file = st.file_uploader("Upload PCB RFQ PDF", type=["pdf"])

# ============================================
# 📘 PDF → Images
# ============================================
def pdf_to_images(pdf_bytes, dpi=300):
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in pdf:
        pix = page.get_pixmap(dpi=dpi)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)
    return images

# ============================================
# 🔄 Auto-Rotate
# ============================================
def auto_rotate(image):
    try:
        osd = pytesseract.image_to_osd(image)
        angle = int(osd.split("Rotate:")[1].split("\n")[0].strip())
        return image.rotate(-angle, expand=True)
    except:
        return image

# ============================================
# 📝 OCR Extraction
# ============================================
def extract_text(images):
    text = ""
    for idx, img in enumerate(images):
        rotated = auto_rotate(img)
        ocr_text = pytesseract.image_to_string(rotated)
        text += f"\n\n===== PAGE {idx+1} =====\n{ocr_text}"
    return text


# ============================================
# 🤖 GPT-4o Field Mapping
# ============================================
def gpt40_map_fields(extracted_text):

    prompt = f"""
You are an expert PCB manufacturing engineer.

Extract ONLY the following RFQ fields from the extracted text:

- Customer Name
- Final Finish
- Soldermask
- Soldermask Thickness
- PCB Thickness (mm)
- PCB Single Width (X mm)
- PCB Single Height (Y mm)
- Array Supply Width (X mm)
- Array Supply Height (Y mm)
- Supply Format
- Outer Layer Cu Thickness
- Inner Layer Cu Thickness
- Layer Count
- Impedance Control
- Board Category
- Order Format
- Item Group ID
- Silkscreen Color
- Regulatory Requirements

Mapping Rules:
1. “SILKSCREEN : WHITE” → Silkscreen Color = WHITE
2. If text contains “RoHS”, “RoHS compliant”, “RoHS 2011/65/EU” → Regulatory Requirements = RoHS
3. If any field is missing, set it as empty string.

Return JSON strictly in this structure:

{{
  "customer_name": "",
  "final_finish": "",
  "soldermask": "",
  "soldermask_thickness": "",
  "pcb_thickness_mm": "",
  "pcb_single_width_mm": "",
  "pcb_single_height_mm": "",
  "array_supply_width_mm": "",
  "array_supply_height_mm": "",
  "supply_format": "",
  "outer_layer_cu_thickness": "",
  "inner_layer_cu_thickness": "",
  "layer_count": "",
  "impedance_control": "",
  "board_category": "",
  "order_format": "",
  "item_group_id": "",
  "silkscreen_color": "",
  "regulatory_requirements": ""
}}

Here is the extracted text:
-------------------------
{extracted_text}
-------------------------

Only return VALID JSON. No explanation.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


# ============================================
# 🚀 Main App Logic
# ============================================
if uploaded_file and st.button("Extract & Auto-Fill RFQ"):

    st.info("⏳ Running OCR…")

    pdf_bytes = uploaded_file.read()
    images = pdf_to_images(pdf_bytes)
    extracted_text = extract_text(images)

    with st.expander("📘 Extracted Text"):
        st.text(extracted_text)

    st.info("🤖 Mapping fields using GPT-4o…")

    mapped = gpt40_map_fields(extracted_text)

    st.success("🎉 GPT-4o Successfully Mapped RFQ Fields!")

    st.subheader("📝 Auto-Filled RFQ Form (Editable)")

    final_output = {}

    # Split keys for two column UI
    keys = list(mapped.keys())
    left_keys = keys[:10]
    right_keys = keys[10:]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔹 RFQ Parameters (Part 1)")
        for key in left_keys:
            value = st.text_input(key.replace("_", " ").title(), mapped[key])
            final_output[key] = value

    with col2:
        st.markdown("### 🔹 RFQ Parameters (Part 2)")
        for key in right_keys:
            value = st.text_input(key.replace("_", " ").title(), mapped[key])
            final_output[key] = value

    st.subheader("📤 Final JSON Output")
    st.json(final_output)
