from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", size=10)

metadata = {
    "Field 1": "Value 1",
    "Field 2": "Value 2",
    "Field 3": "Value 3",
    "Field 4": "Value 4",
}
values = list(metadata.items())
rows = [values[i : i + 2] for i in range(0, len(values), 2)]
label = "some label"
value = "some value"
with pdf.table(col_widths=(40), align="L") as table:
    for pair in rows:
        row = table.row()
        for label, value in pair:
            label_text = f"{label}:"
            value_text = value
            row.cell(label_text, border=False)
            row.cell(text=f"--{value_text}--", border=False)
            # If odd number of fields, pad the last line
            if len(pair) < 2:
                row.cell("")

pdf.output("test.pdf")
