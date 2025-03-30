import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


app = FastAPI()


origins = [
    "http://localhost:5173",  # If you're running React locally
    "https://your-frontend-domain.com"  # If deployed
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only specific frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)
class questionRequest(BaseModel):
    exam:str
    subject:str
    topic:str
    difficulty:str

def generate_question(exam ,subject, topic , difficulty):
    prompt = f"""
   Generate 10 multiple-choice questions (MCQs) in JSON format for the {exam} exam. Focus on the most important and frequently asked questions from previous years. Each question should be highly relevant to the exam syllabus and difficulty level. Structure the JSON output as follows
   in the correct_answer do not give the answer the option number , give the correct answer the string which was passed in the options array:
    Subject: {subject}
    Topic: {topic}
    Difficulty: {difficulty}

    Return JSON format:
    {{
        "questions": [
            {{
                "question": "Question text?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option B"
            }},
            ...
        ]
    }}
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-questions/")
async def get_questions(request: questionRequest):
    response = generate_question(request.exam, request.subject, request.topic, request.difficulty)
    try:
        # Extract the JSON string inside the triple backticks
        extracted_json = re.sub(r"```json|```", "", response)
        # Parse the JSON string into a dictionary
        parsed_data = json.loads(extracted_json)
        return {"success":True, "questions" :parsed_data}
    except Exception as e:
        return {"success":False,"error": "Invalid JSON format", "message": str(e)}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use Render's PORT environment variable
    uvicorn.run(app, host="0.0.0.0", port=port)

