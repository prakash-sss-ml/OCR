import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="RFQ Auto-Fill Form", layout="wide")

st.title("📄 Request for Quote (RFQ) Form")
st.write("Upload your RFQ PDF to auto-fill fields automatically.")

# -------------------------------
# 1️⃣ Extract text from PDF
# -------------------------------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in pdf:
        text += page.get_text("text")
    return text


# -------------------------------
# 2️⃣ Parse RFQ fields (basic regex rules)
# -------------------------------
def parse_rfq_data(text: str) -> dict:
    """
    Enhanced extraction with flexible pattern matching
    """

    def find_any(patterns):
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return ""

    return {
        "Customer Name": find_any([
            r"Customer\s*Name[:\-]?\s*(.*)",
            r"Customer[:\-]?\s*(.*)",
            r"Client[:\-]?\s*(.*)"
        ]),
        "Final Finish": find_any([
            r"Final\s*Finish[:\-]?\s*(.*)",
            r"Finish\s*Type[:\-]?\s*(.*)",
            r"Finish[:\-]?\s*(.*)"
        ]),
        "Soldermask": find_any([
            r"Soldermask[:\-]?\s*(.*)",
            r"Mask\s*Color[:\-]?\s*(.*)",
            r"Color[:\-]?\s*(.*)"
        ]),
        "Soldermask Thickness": find_any([
            r"Soldermask\s*Thickness[:\-]?\s*(.*)",
            r"Mask\s*Thick[:\-]?\s*(.*)",
            r"Mask\s*Thickness[:\-]?\s*(.*)"
        ]),
        "PCB Thickness (mm)": find_any([
            r"PCB\s*Thickness[:\-]?\s*(.*)",
            r"Board\s*Thickness[:\-]?\s*(.*)"
        ]),
        "PCB Single Width (X mm)": find_any([
            r"Single\s*Width[:\-]?\s*(.*)",
            r"Single\s*X[:\-]?\s*(.*)"
        ]),
        "PCB Single Height (Y mm)": find_any([
            r"Single\s*Height[:\-]?\s*(.*)",
            r"Single\s*Y[:\-]?\s*(.*)"
        ]),
        "Array Supply Width (X mm)": find_any([
            r"Array\s*Width[:\-]?\s*(.*)",
            r"Array\s*X[:\-]?\s*(.*)"
        ]),
        "Array Supply Height (Y mm)": find_any([
            r"Array\s*Height[:\-]?\s*(.*)",
            r"Array\s*Y[:\-]?\s*(.*)"
        ]),
        "Supply Format": find_any([
            r"Supply\s*Format[:\-]?\s*(.*)",
            r"Delivery\s*Form[:\-]?\s*(.*)"
        ]),
        "Outer Layer Cu Thickness": find_any([
            r"Outer\s*Layer\s*Cu\s*Thickness[:\-]?\s*(.*)",
            r"Outer\s*Cu[:\-]?\s*(.*)"
        ]),
        "Inner Layer Cu Thickness": find_any([
            r"Inner\s*Layer\s*Cu\s*Thickness[:\-]?\s*(.*)",
            r"Inner\s*Cu[:\-]?\s*(.*)"
        ]),
        "Layer Count": find_any([
            r"Layer\s*Count[:\-]?\s*(.*)",
            r"Layers[:\-]?\s*(.*)"
        ]),
        "Impedance Control": find_any([
            r"Impedance\s*Control[:\-]?\s*(.*)",
            r"Impedance[:\-]?\s*(.*)"
        ]),
        "Board Category": find_any([
            r"Board\s*Category[:\-]?\s*(.*)",
            r"Category[:\-]?\s*(.*)"
        ]),
        "Order Format": find_any([
            r"Order\s*Format[:\-]?\s*(.*)",
            r"File\s*Type[:\-]?\s*(.*)"
        ]),
        "Item Group ID": find_any([
            r"Item\s*Group\s*ID[:\-]?\s*(.*)",
            r"Group\s*ID[:\-]?\s*(.*)"
        ]),
    }


# -------------------------------
# 3️⃣ File upload
# -------------------------------
uploaded_file = st.file_uploader("📎 Upload RFQ PDF", type=["pdf"])

data = {}
if uploaded_file:
    file_bytes = uploaded_file.read()
    text = extract_text_from_pdf(file_bytes)
    data = parse_rfq_data(text)
    st.success("✅ PDF processed successfully. Auto-filled data below:")

# -------------------------------
# 4️⃣ Two-column form layout
# -------------------------------
st.divider()
st.subheader("🧾 RFQ Form")

col1, col2 = st.columns(2)

with col1:
    customer_name = st.text_input("Customer Name", value=data.get("Customer Name", ""))
    final_finish = st.text_input("Final Finish", value=data.get("Final Finish", ""))
    soldermask = st.text_input("Soldermask", value=data.get("Soldermask", ""))
    soldermask_thickness = st.text_input("Soldermask Thickness", value=data.get("Soldermask Thickness", ""))
    pcb_thickness = st.text_input("PCB Thickness (mm)", value=data.get("PCB Thickness (mm)", ""))
    pcb_single_width = st.text_input("PCB Single Width (X mm)", value=data.get("PCB Single Width (X mm)", ""))
    pcb_single_height = st.text_input("PCB Single Height (Y mm)", value=data.get("PCB Single Height (Y mm)", ""))
    array_width = st.text_input("Array Supply Width (X mm)", value=data.get("Array Supply Width (X mm)", ""))
    array_height = st.text_input("Array Supply Height (Y mm)", value=data.get("Array Supply Height (Y mm)", ""))

with col2:
    supply_format = st.text_input("Supply Format", value=data.get("Supply Format", ""))
    outer_layer = st.text_input("Outer Layer Cu Thickness", value=data.get("Outer Layer Cu Thickness", ""))
    inner_layer = st.text_input("Inner Layer Cu Thickness", value=data.get("Inner Layer Cu Thickness", ""))
    layer_count = st.text_input("Layer Count", value=data.get("Layer Count", ""))
    impedance_control = st.text_input("Impedance Control", value=data.get("Impedance Control", ""))
    board_category = st.text_input("Board Category", value=data.get("Board Category", ""))
    order_format = st.text_input("Order Format", value=data.get("Order Format", ""))
    item_group = st.text_input("Item Group ID", value=data.get("Item Group ID", ""))

st.divider()

if st.button("Submit RFQ"):
    result = {
        "Customer Name": customer_name,
        "Final Finish": final_finish,
        "Soldermask": soldermask,
        "Soldermask Thickness": soldermask_thickness,
        "PCB Thickness (mm)": pcb_thickness,
        "PCB Single Width (X mm)": pcb_single_width,
        "PCB Single Height (Y mm)": pcb_single_height,
        "Array Supply Width (X mm)": array_width,
        "Array Supply Height (Y mm)": array_height,
        "Supply Format": supply_format,
        "Outer Layer Cu Thickness": outer_layer,
        "Inner Layer Cu Thickness": inner_layer,
        "Layer Count": layer_count,
        "Impedance Control": impedance_control,
        "Board Category": board_category,
        "Order Format": order_format,
        "Item Group ID": item_group,
    }
    st.success("✅ RFQ Submitted Successfully!")
    st.json(result)
