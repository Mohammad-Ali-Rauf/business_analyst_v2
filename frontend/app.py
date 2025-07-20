import gradio as gr
import requests
import uuid

SESSION_TOKEN=uuid.uuid4()
API_URL = "http://localhost:8000/generate_from_text"

def generate_user_story(text: str):
    payload = {"text": text, "token": SESSION_TOKEN}
    try:
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        result=response.json()
        story = result["story"]
        if isinstance(story, dict) and "content" in story:
            return story["content"]
        return str(story)
    except Exception as e:
        return f"Error: {e}"

with gr.Blocks() as demo:
    gr.Markdown("# Agile User Story Generator")
    feature_input = gr.Textbox(label="Feature or Requirement", lines=5, placeholder="Type your feature here...")
    output = gr.Markdown()
    
    btn = gr.Button("Generate User Story")
    btn.click(generate_user_story, inputs=feature_input, outputs=output)

if __name__ == "__main__":
    demo.launch(share=True)