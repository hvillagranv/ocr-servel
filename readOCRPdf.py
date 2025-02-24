#Es necesario instalar las librerías para leer pdf
#Copiar en terminal: pip install pymupdf pytesseract pillow
#Instalar Teseract
#Windows: Download from Tesseract installer.
#Linux: sudo apt install tesseract-ocr.
#Mac: brew install tesseract.

#OpenCV
#pip install opencv-python

#Revisar formatos de cada archivo, en este caso se considera el archivo de la presidencial de 1925

#Fuente de datos electorales
#https://www.servel.cl/resultados-electorales-1925-1973/

import re
import pandas as pd
import fitz
import pytesseract
import io
import cv2
import numpy as np
from PIL import Image
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = []
    
    for page in doc:
        pix = page.get_pixmap(dpi=400, colorspace=fitz.csGRAY)
        img_bytes = pix.tobytes("png") 
        
        img = Image.open(io.BytesIO(img_bytes))
        img_np = np.array(img)
        
        img_np = cv2.medianBlur(img_np, 1)
        _, img_np = cv2.threshold(img_np, 150, 255, cv2.THRESH_BINARY)
        
        # Configurar parámetros de Tesseract para tablas
        custom_config = r'--oem 3 --psm 6 -l spa'
        text = pytesseract.image_to_string(img_np, config=custom_config)
        
        full_text.append(text)
    
    return "\n".join(full_text)

def parse_text(full_text):
    lines = [line.strip() for line in full_text.split('\n') if line.strip()]
    data = []
    current_province = None

    total_pais_regex = re.compile(
        r'TOTAL\s+PA[IÍ]S.*?(\d{1,3}(?:\.\d{3})*).*?(\d{1,3}(?:\.\d{3})*).*?(\d+).*?(\d{1,3}(?:\.\d{3})*)',
        re.IGNORECASE
    )

    table_pattern = re.compile(
        r'^([A-ZÁÉÍÓÚ\s]+?)\s+(\d{1,3}(?:\.\d{3})*)\s+(\d{1,3}(?:\.\d{3})*)\s+(\d{1,3}(?:\.\d{3})*)\s+(\d{1,3}(?:\.\d{3})*)$'
    )

    for line in lines:
        # Detectar filas de tabla
        match = table_pattern.match(line)
        if match:
            parts = match.groups()
            if "TOTAL PROV" in line:
                data.append({
                    'Provincia': current_province,
                    'Departamento': 'TOTAL PROVINCIA',
                    'Emiliano Figueroa': parts[1].replace('.', ''),
                    'José Santos Salas': parts[2].replace('.', ''),
                    'Votos Nulos/Blancos': parts[3].replace('.', ''),
                    'Total de Votantes': parts[4].replace('.', '')
                })
            else:
                data.append({
                    'Provincia': parts[0],
                    'Departamento': '',
                    'Emiliano Figueroa': parts[1].replace('.', ''),
                    'José Santos Salas': parts[2].replace('.', ''),
                    'Votos Nulos/Blancos': parts[3].replace('.', ''),
                    'Total de Votantes': parts[4].replace('.', '')
                })
            continue

        # Detectar provincias (versión mejorada)
        if re.match(r'PROV\.?\s+[A-Z]', line):
            current_province = re.sub(r'PROV\.?\s+|\d+', '', line).strip()
            continue

        # Detectar total nacional
        if "TOTAL PAIS" in line:
            line_clean = re.sub(r'[^\d\s]', '', line)  # Solo dígitos y espacios
            parts = [p for p in line_clean.split() if p.isdigit()]
            
            if len(parts) >= 4:
                try:
                    data.append({
                        'Provincia': 'TOTAL PAÍS',
                        'Departamento': '',
                        'Emiliano Figueroa': int(parts[0]),
                        'José Santos Salas': int(parts[1]),
                        'Votos Nulos/Blancos': int(parts[2]),
                        'Total de Votantes': int(parts[3])
                    })
                except IndexError:
                    print(f"Formato inválido en línea: {line}")
            continue

    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Convertir a números
    numeric_cols = ['Emiliano Figueroa', 'José Santos Salas', 
                   'Votos Nulos/Blancos', 'Total de Votantes']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    
    return df

# Uso
pdf_path = "Fuentes/1925-Presidente.pdf"
full_text = extract_pdf(pdf_path)
results_df = parse_text(full_text)

if not results_df.empty:
    results_df.to_csv('resultados_completos.csv', index=False)
    print("Extracción exitosa. Columnas obtenidas:")
    print(results_df.columns.tolist())
    print("\nPrimeras filas:")
    print(results_df)
else:
    print("Error: Revisar configuración de OCR o calidad del PDF")