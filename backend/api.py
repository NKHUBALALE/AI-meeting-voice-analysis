from fastapi import FastAPI, UploadFile, File
import shutil
import subprocess
import json

app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    
    # Save uploaded file
    file_path = "input.webm"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run your script
    result = subprocess.run(
        ["python", "voice_analysis.py"],
        capture_output=True,
        text=True
    )

    return {
        "output": result.stdout
    }