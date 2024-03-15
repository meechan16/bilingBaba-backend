from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO


'''
{

    // 
    date
    [product name, quantity, unit price, total price]
    sub total without tax
    tax (1 model)




    // generated 
    invoice number    
    }
'''

predata = {
    "name": "Billing Baba",
    "email": "support@billingbaba.com",
    "phone": "+91 100XXXXXXX"
}


# def create_tax_invoice_pdf(filename):
def create_tax_invoice_pdf(data):
    # Create canvas
    buffer = BytesIO()

    # Create canvas
    c = canvas.Canvas(buffer, pagesize=letter)
    # c = canvas.Canvas(filename, pagesize=letter)

    # Set up fonts and styles
    c.setFont("Helvetica", 10)  # Set font and size for business details
    c.setFillColorRGB(0, 0, 0)  # Set color to black

    # Business details
    c.drawString(50, 750, predata['name'])
    c.drawString(50, 735, "Phone: "+predata["phone"])
    c.drawString(50, 720, "Email: "+predata["email"])

    # Logo
    logo_path = "backend/logo.jpg"  # Replace with the path to your logo image
    # Adjust coordinates and size as needed
    c.drawImage(logo_path, x=450, y=720, width=100, height=50)

    # Draw line
    c.setStrokeColorRGB(0, 0, 0)  # Set line color to black
    c.line(50, 710, 550, 710)

    # Heading
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0, 0, 0)  # Reset color to black
    c.drawCentredString(300, 680, "Tax Invoice")

    # Purple line
    c.setStrokeColorRGB(0.5, 0, 0.5)  # Set line color to purple
    c.setLineWidth(3)  # Set line thickness
    c.line(50, 660, 550, 660)

    # Invoice details
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)  # Reset color to black
    c.drawString(50, 630, "Invoice Details")
    c.setFont("Helvetica", 10)
    c.drawString(50, 615, "Invoice No.: "+str(data['invoice_number']))
    c.drawString(50, 600, "Date: "+data["invoice_date"])

    c.drawString(
        50, 585, "Description: "+data["description"])

    # Draw table
    table_y = 540
    c.setFillColorRGB(0.5, 0, 0.5)  # Set fill color to purple
    c.rect(50, table_y, 500, 20, fill=1)  # Filled rectangle for header row
    c.setFillColorRGB(1, 1, 1)  # Set fill color to white for text
    c.setFont("Helvetica-Bold", 10)
    c.drawString(55, table_y + 5, "Description")
    c.drawString(255, table_y + 5, "Quantity")
    c.drawString(305, table_y + 5, "Unit Price")
    c.drawString(405, table_y + 5, "Total Price")

    # Dummy data for table
    c.setFillColorRGB(0, 0, 0)  # Reset fill color to black
    y = table_y - 20
    # for _ in range(7):
    #     c.drawString(55, y, "Product Name")
    #     c.drawString(255, y, "2")
    #     c.drawString(305, y, "$25.00")
    #     c.drawString(405, y, "$50.00")
    #     y -= 20
    for i in data['items']:
        c.drawString(55, y, str(i["item"]))
        c.drawString(255, y, str(i["qty"]))
        c.drawString(305, y, str(i["price_per_unit"]))
        c.drawString(405, y, str(i["amount"]))
        y -= 20

    # Adding space after the table
    content_y = y - 40

    # Additional text
    invoice_amount_text = "Total Amount: "+str(data["total"])
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, content_y, "Invoice Summary:")
    c.setFont("Helvetica", 10)
    c.drawString(50, content_y - 15, invoice_amount_text)

    # Values on the right side in table format
    data = [
        ("Sub Total", "₹ "+str(int(data['total']) - int(data['total_tax']))),
        ("Tax (0%)", "₹ "+str(data['total_tax'])),
        ("Total", "₹ "+str(data['total'])),
        ("Paid", "₹ 0.00"),
        ("Balance Due", "₹ "+str(data['total']))
    ]
    y_offset = 0
    for item, value in data:
        c.drawString(300, content_y + y_offset, item)
        c.drawRightString(500, content_y + y_offset, value)
        y_offset -= 15

    # Signature and authorization
    c.line(50, content_y - 130, 300, content_y - 130)  # Line for signature
    c.drawString(50, content_y - 150, "Authorized Signature")

    # Save the PDF
    c.save()

    buffer.seek(0)

    # Return the PDF file as a response
    return buffer
    # return send_file(buffer, as_attachment=True, attachment_filename='styled_tax_invoice.pdf', mimetype='application/pdf')


# Create tax invoice PDF
# create_tax_invoice_pdf("styled_tax_invoice.pdf")
