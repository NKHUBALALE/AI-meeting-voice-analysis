# AI Meeting Voice Analyzer

An AI-powered web application that analyzes meeting recordings to
provide insights into communication style, including volume, pace, tone,
confidence, and key speaking patterns.

------------------------------------------------------------------------

## Live Demo

https://ai-meeting-voice-analysis.vercel.app

------------------------------------------------------------------------

## Features

-   Upload audio/video recordings
-   Analyze communication metrics:
    -   Volume
    -   Speaking pace (WPM)
    -   Tone
    -   Confidence score
-   AI-generated communication profile
-   Personalized feedback suggestions
-   Keyword extraction with frequency counts
-   Chrome extension for recording meetings directly

------------------------------------------------------------------------

## Project Structure

    AI-meeting-voice-analysis/
    │
    ├── backend/
    ├── frontend/
    ├── meeting-recorder-extension/
    ├── requirements.txt

------------------------------------------------------------------------

## Tech Stack

### Frontend

-   HTML, CSS, JavaScript
-   Deployed on Vercel

### Backend

-   Python (FastAPI)
-   Uvicorn
-   Speech processing and NLP

### Tools

-   Ngrok (local backend exposure)
-   FFmpeg (audio/video processing)

------------------------------------------------------------------------

## How It Works

    User uploads recording
            ↓
    Frontend (Vercel)
            ↓
    Ngrok tunnel
            ↓
    FastAPI backend
            ↓
    Audio processing + AI analysis
            ↓
    Results returned to UI

------------------------------------------------------------------------

## Running Locally

### 1. Clone the repository

    git clone https://github.com/NKHUBALALE/AI-meeting-voice-analysis.git
    cd AI-meeting-voice-analysis

------------------------------------------------------------------------

### 2. Setup backend(windows)
        
    cd backend
    python -m venv venv
    venv\Scripts\activate   
    pip install -r ../requirements.txt

------------------------------------------------------------------------

### 3. Run backend server

    uvicorn api:app --host 0.0.0.0 --port 8000

------------------------------------------------------------------------

### 4. Start ngrok

    ngrok http 8000

Copy the generated URL (e.g. https://xxxxx.ngrok-free.dev)

------------------------------------------------------------------------

### 5. Connect frontend to backend

Open:

    frontend/index.html

Update this line:

``` javascript
fetch("https://your-ngrok-url.ngrok-free.dev/analyze")
```

Replace with your ngrok URL.

------------------------------------------------------------------------

### 6. Run the frontend

-   Open `frontend/index.html` in your browser
    OR
-   Deploy the frontend using Vercel

------------------------------------------------------------------------

## Instructions for Forking This Repository

### 1. Fork and clone

    git clone https://github.com/YOUR_USERNAME/AI-meeting-voice-analysis.git
    cd AI-meeting-voice-analysis

------------------------------------------------------------------------

### 2. Setup backend

    cd backend
    python -m venv venv
    venv\Scripts\activate
    pip install -r ../requirements.txt

------------------------------------------------------------------------

### 3. Run backend

    uvicorn api:app --host 0.0.0.0 --port 8000

------------------------------------------------------------------------

### 4. Start ngrok

    ngrok http 8000

------------------------------------------------------------------------

### 5. Update frontend API URL

Edit:

    frontend/index.html

Replace:

``` javascript
fetch("https://your-ngrok-url.ngrok-free.dev/analyze")
```

------------------------------------------------------------------------

### 6. Test the app

-   Open frontend in browser
-   Upload a recording
-   View analysis results

------------------------------------------------------------------------

## Current Limitations

-   Large video files may cause slow processing
-   Requires backend and ngrok to be running locally
-   Video uploads are not optimized

------------------------------------------------------------------------

## Future Improvements

-   Convert video to audio automatically
-   Deploy backend to remove ngrok dependency
-   Add charts and analytics
-   Drag-and-drop upload
-   History tracking

------------------------------------------------------------------------

## Author

Nkhubalale Emmanuel Nkadimeng

- GitHub: [NKHUBALALE](https://github.com/NKHUBALALE)
- LinkedIn: [Nkhubalale Emmanuel Nkadimeng](https://www.linkedin.com/in/nkhubalale-emmanuel-nkadimeng/?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3B%2F2wPKaEQQjSG4Gfls%2Fe9TA%3D%3D)
- X/Twitter: [NKHUBALALE](https://x.com/NkhubalaleN)
- Kaggle: [NKHUBALALE](https://www.kaggle.com/nkhubalale
)

