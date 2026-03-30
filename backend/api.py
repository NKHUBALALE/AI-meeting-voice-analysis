from fastapi import FastAPI, UploadFile, File
import shutil
import os
from voice_analysis import analyze_video

from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    file_path = "input.webm"

    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Call the function directly 
        result = analyze_video(file_path)

        return result

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Clean up uploaded video
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass