import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

prompt_template = """
You are an expert Agile product owner.

Based on the following input, write a user story in this format:

As a [actor],  
I want to [action],  
So that [benefit].

Include 2–3 acceptance criteria.

Input:
{input}
"""

def get_user_story_agent():
    model = genai.GenerativeModel('gemini-pro')

    def run_agent(feature_input: str):
        final_prompt = prompt_template.format(input=feature_input)
        response = model.generate_content(final_prompt)
        return response.text.strip()
    
    return run_agent