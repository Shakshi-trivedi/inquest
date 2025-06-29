from google import genai
from django.shortcuts import render
import fitz
from typing import Dict

def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def text_to_text(request):
    api_key="AIzaSyCAwsOgg8cslyQ-5tTxRaBijj1RwkZm4sQ"
    client = genai.Client(api_key = api_key)

    return render()

from pydantic import BaseModel
from typing import List

class InterviewQuestion(BaseModel):
    question: str

def text_to_text_structured_output(user_prompt):
    api_key="AIzaSyCAwsOgg8cslyQ-5tTxRaBijj1RwkZm4sQ"
    client = genai.Client(api_key = api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": List[InterviewQuestion],
        },
    )
    questions: List[InterviewQuestion] = response.parsed
    question_list = []
    for q in questions:
        question_list.append(q.question)
    return question_list



def text_to_structured_questions(user_prompt: str) -> List[str]:
    api_key="AIzaSyCAwsOgg8cslyQ-5tTxRaBijj1RwkZm4sQ"
    client = genai.Client(api_key=api_key)

    schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "question": {"type": "STRING"}
            },
            "required": ["question"]
        }
    }

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": schema,
        },
    )

    data = response.parsed
    return [item["question"] for item in data]


def evaluate_response(user_prompt: str) -> Dict[str, float]:
    api_key = "AIzaSyCAwsOgg8cslyQ-5tTxRaBijj1RwkZm4sQ"
    client = genai.Client(api_key=api_key)

    schema = {
        "type": "OBJECT",
        "properties": {
            "total_questions": {"type": "STRING"},
            "answered": {"type": "STRING"},
            "confidence": {"type": "STRING"},
            "performance": {"type": "STRING"},
        },
        "required": ["total_questions", "answered", "confidence", "performance"]
    }

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": schema,
            "system_instruction": (
                "Your task is to extract and provide 'total_questions', 'answered', "
                "'confidence', and 'performance' based on the user's resume and how they "
                "answered those questions. Ensure the output is strictly in the defined JSON schema."
            ),
        },
    )

    return response.parsed