from fastapi import FastAPI, UploadFile, File, Form
from agents.user_story_agent import get_user_story_agent
import uuid
from utils.audio_to_text import transcribe_audio

app = FastAPI()

@app.post("/generate_from_text")
async def generate_user_story(text: str = Form(...), token: str = Form(...)):
    agent = get_user_story_agent(token)
    story = agent(text)
    return {"story": story}

@app.post("/generate_from_audio")
async def generate_user_story_from_audio(file: UploadFile = File(...), token: str = Form(...)):
    audio_path = "temp_audio.wav"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    transcription = transcribe_audio(audio_path)
    agent = get_user_story_agent(token)
    story = agent(transcription)
    return {"transcription": transcription, "story": story}

@app.get("/get_session_token")
async def get_session_token():
    return {"token": str(uuid.uuid4())}