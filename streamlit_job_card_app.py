# app.py
dispatch_loc = st.text_input("Dispatch Location")

# Goods Received Table
st.subheader("Goods Received From Vendor")
grv_table = st.data_editor(pd.DataFrame({
"Date": [""],
"Qty Received": [0],
"OK Qty": [0],
"Rejected Qty": [0],
"Remarks": [""],
"QC Approved By": [""]
}))

# Generate PDF
st.subheader("Generate Job Card PDF")

def make_pdf():
buffer = BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=A4)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph(f"<b>{company_name}</b><br/>{company_address}", styles['Title']))
story.append(Spacer(1, 12))

story.append(Paragraph(f"<b>Job Card No:</b> {job_no}", styles['Normal']))
story.append(Paragraph(f"<b>Date:</b> {date}", styles['Normal']))
story.append(Paragraph(f"<b>Vendor:</b> {vendor_name}", styles['Normal']))
story.append(Spacer(1, 12))

story.append(Paragraph("<b>Item Details:</b>", styles['Heading2']))
story.append(Paragraph(item_table.to_html(), styles['Normal']))

story.append(Paragraph("<b>Material Issued:</b>", styles['Heading2']))
story.append(Paragraph(material_table.to_html(), styles['Normal']))

story.append(Paragraph("<b>Operations Selected:</b> " + ", ".join([op for op, val in op_selected.items() if val]), styles['Normal']))

if show_machine:
story.append(Paragraph(f"Machine Type: {machine_type}", styles['Normal']))
story.append(Paragraph(f"Cycle Time: {cycle_time}", styles['Normal']))

story.append(Paragraph("<b>Quality Instructions:</b>", styles['Heading2']))
story.append(Paragraph(f"Tolerance: {tolerance}", styles['Normal']))
story.append(Paragraph(f"Finish: {finish}", styles['Normal']))

story.append(Paragraph("<b>Delivery Details:</b>", styles['Heading2']))
story.append(Paragraph(f"Expected Date: {exp_date}", styles['Normal']))
story.append(Paragraph(f"Dispatch: {dispatch_loc}", styles['Normal']))

story.append(Paragraph("<b>GRN Table:</b>", styles['Heading2']))
story.append(Paragraph(grv_table.to_html(), styles['Normal']))

if qr_img:
temp = BytesIO()
qr_img.save(temp, format="PNG")
temp.seek(0)
img = Image.open(temp)
story.append(Spacer(1, 20))
story.append(Paragraph("QR Code:", styles['Heading2']))

doc.build(story)
buffer.seek(0)
return buffer

if st.button("Generate PDF"):
pdf_bytes = make_pdf().getvalue()
st.download_button("Download Job Card PDF", pdf_bytes, file_name="job_card.pdf", mime="application/pdf")
