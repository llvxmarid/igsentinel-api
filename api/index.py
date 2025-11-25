from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "IG Sentinel API is running", "version": "1.0"}
