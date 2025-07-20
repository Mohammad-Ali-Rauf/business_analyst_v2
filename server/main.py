from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from agents.user_story_agent import get_user_story_agent
from utils.audio_to_text import transcribe_audio
import tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate_from_text")
async def generate_user_story(text: str = Form(...), token: str = Form(...)):
    agent = get_user_story_agent(token)
    story = agent(text)
    return {"story": story}

@app.post("/generate_from_audio")
async def generate_user_story_from_audio(file: UploadFile = File(...), token: str = Form(...)):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        tmp.write(await file.read())
        tmp.flush()
        transcription = transcribe_audio(tmp.name)
        agent = get_user_story_agent(token)
        story = agent(transcription)
    return {"transcription": transcription, "story": story}