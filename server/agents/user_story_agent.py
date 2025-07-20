import os
from dotenv import load_dotenv
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import google.generativeai as genai

from utils.memory_manager import get_last_n_memories, save_memory_for_token

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

prompt_template = PromptTemplate.from_template("""
You are an expert Agile Product Owner and Business Analyst.

Below is a summary of our prior conversation (if any), followed by the new input:

---

**Previous Context:**  
{history}

---

**New Feature Input:**  
{feature_input}

---

Your task is to generate a well-structured and detailed user story document based on the new input, considering any relevant prior context.
Please produce a user story document that takes into account any relevant past features and context. If this story builds upon an earlier one, reference it naturally.

Strictly follow this format:

User Story
                                                
As a [actor],  
I want to [action],  
So that [benefit].

Context 
Give 2–3 lines of extra background explaining the story’s business value, technical considerations, or UX importance.

Acceptance Criteria
- Clear  
- Testable  
- Functional requirements only

Security Requirements (if applicable)  
- Mention access control, verification, rate limits, etc.

Test Scenarios
- Simple bullet-style test cases covering the flow

DO NOT add explanations or commentary. ONLY return this formatted output in MARKDOWN.
""")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GEMINI_API_KEY, temperature=0.7)


def get_user_story_agent(token: str):
    def run_agent(feature_input: str):
        # Fetch last 5 memories for context or fallback text
        past_memories = get_last_n_memories(token, n=5)
        history_text = "\n---\n".join(past_memories) if past_memories else "No prior context available."

        # Build prompt with prior context + new input
        prompt = prompt_template.format(history=history_text, feature_input=feature_input)

        # Call LLM with prompt
        response = llm.invoke(prompt)

        if hasattr(response, 'text'):
            clean_md = response.text() if callable(response.text) else response.text
        elif isinstance(response, dict) and "text" in response:
            clean_md = response["text"]
        else:
            clean_md = str(response)

        if not isinstance(clean_md, str):
            print("💥 CLEAN_MD was not string:", type(clean_md))
            clean_md = str(clean_md)

        clean_md = re.sub(r"^```(?:markdown)?\n?", "", clean_md)
        clean_md = re.sub(r"\n?```$", "", clean_md)

        save_memory_for_token(token, feature_input)
        save_memory_for_token(token, clean_md.strip())

        return clean_md.strip()

    return run_agent