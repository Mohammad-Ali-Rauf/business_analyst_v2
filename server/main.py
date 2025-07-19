from fastapi import FastAPI, UploadFile, File, Form
from agents.user_story_agent import get_user_story_agent
from utils.audio_to_text import transcribe_audio

app = FastAPI()
agent = get_user_story_agent()

@app.post("/generate_from_text/")
async def generate_user_story(text: str = Form(...)):
    story = agent(text)
    return {"story": story}

@app.post("/generate_from_audio/")
async def generate_user_story_from_audio(file: UploadFile = File(...)):
    file_location = "temp_audio.wav"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    transcription = transcribe_audio(file_location)
    story = agent(transcription)
    return {"transcription": transcription, "story": story}