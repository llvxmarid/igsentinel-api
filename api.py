import base64
import io
import json
from PIL import Image
import pytesseract
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pdf2image import convert_from_bytes

app = FastAPI()

def analyze_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))

    # OCR METİN ÇIKARMA
    text = pytesseract.image_to_string(img, lang="tur")

    # Basit Fraud Analizi
    width, height = img.size
    fraud_score = 0

    # Düşük çözünürlük şüpheli
    if width < 600 or height < 600:
        fraud_score += 25

    # Aşırı keskinlik / gradient yoksa montaj olabilir
    pixels = list(img.getdata())
    avg = sum(sum(p) for p in pixels) / (len(pixels) * 3)
    if avg < 30 or avg > 230:
        fraud_score += 20

    # En basit banka kontrolü
    is_bank_format = ("IBAN" in text.upper()) or ("TL" in text.upper())

    result = {
        "ocr_text": text,
        "iban": extract_iban(text),
        "tutar": extract_amount(text),
        "tarih": extract_date(text),
        "fraud_score": fraud_score,
        "bank_format_ok": is_bank_format,
        "status": "ŞÜPHELİ" if fraud_score > 40 else "MUHTEMEL" if fraud_score > 20 else "MUHTEMELİN ÜSTÜ"
    }

    return result


def extract_iban(text):
    import re
    match = re.search(r"[T][R]\d{24}", text.replace(" ", ""))
    return match.group() if match else None


def extract_amount(text):
    import re
    match = re.search(r"\d{1,3}(?:\.\d{3})*,\d{2}", text)
    return match.group() if match else None


def extract_date(text):
    import re
    match = re.search(r"\d{2}\.\d{2}\.\d{4}", text)
    return match.group() if match else None


@app.post("/analyze-image")
async def analyze_image_api(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = analyze_image(image_bytes)
    return JSONResponse(result)


@app.post("/analyze-pdf")
async def analyze_pdf_api(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    images = convert_from_bytes(pdf_bytes)
    result = analyze_image(images[0].tobytes())
    return JSONResponse(result)


@app.get("/")
async def root():
    return {"status": "IG Sentinel API Online"}
