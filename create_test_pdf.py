import fitz  # PyMuPDF

def create_dummy_pdf(filename="dummy_contract.pdf"):
    doc = fitz.open()  # new empty PDF
    page = doc.new_page()  # create a new page
    
    # Add some contract text
    page.insert_text((50, 50), "RENTAL AGREEMENT", fontsize=20, fontname="helv", color=(0, 0, 0))
    page.insert_text((50, 100), "This is a dummy contract for testing AI signature detection.", fontsize=12)
    
    # Add a visual signature line for Tenant
    page.insert_text((50, 400), "Tenant Signature:", fontsize=12)
    p1 = fitz.Point(50, 450)
    p2 = fitz.Point(250, 450)
    page.draw_line(p1, p2)
    
    # Add a visual signature line for Landlord
    page.insert_text((350, 400), "Landlord Signature:", fontsize=12)
    p3 = fitz.Point(350, 450)
    p4 = fitz.Point(550, 450)
    page.draw_line(p3, p4)
    
    doc.save(filename)
    print(f"Created {filename}")

if __name__ == "__main__":
    create_dummy_pdf()
