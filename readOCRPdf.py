import fitz 
import pytesseract
from PIL import Image
import io
#Es necesario instalar las librerías para leer pdf
#Copiar en terminal: pip install pymupdf pytesseract pillow
#Instalar Teseract
#Windows: Download from Tesseract installer.
#Linux: sudo apt install tesseract-ocr.
#Mac: brew install tesseract.

#Fuente de datos electorales
#https://www.servel.cl/resultados-electorales-1925-1973/

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pdf_path = "Fuentes/1925-Presidente.pdf"

try:
    doc = fitz.open(pdf_path)
    extracted_text = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300) 
        img = Image.open(io.BytesIO(pix.tobytes("ppm")))
        text = pytesseract.image_to_string(img)
        extracted_text.append(f"Page {page_num+1}:\n{text}\n")
    
    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(extracted_text))
    print(extracted_text)
    print("Text extracted successfully!")

except Exception as e:
    print(f"Error: {e}")