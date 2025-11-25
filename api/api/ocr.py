from fastapi import FastAPI, UploadFile, File
from PIL import Image
import pytesseract
import io

app = FastAPI()

@app.post("/ocr")
async def ocr_read(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image, lang="eng")
    return {"extracted_text": text}
