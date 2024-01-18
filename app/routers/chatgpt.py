from fastapi import Request, HTTPException, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import openai

from dotenv import load_dotenv
import os

load_dotenv("../../.env")


router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_openai_api_key():
    return os.environ.get("OPENAI_API_KEY", "not-set-api-key")

class OpenAIDependency:
   def __init__(self, api_key: str = Depends(get_openai_api_key)):
      self.client = openai.OpenAI(api_key=api_key)

client = OpenAIDependency().client


@router.get('/chatgpt', response_class=HTMLResponse)
async def gpt_page(request: Request):
   return templates.TemplateResponse("gpt.html", {"request": request})

@router.post('/chatgpt', response_class=JSONResponse)
async def chat_with_gpt(request: Request,
                        message: str = Form(...),
              openai_dependency: OpenAIDependency = Depends()):

    print(f"Received message: {message}")
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        stream = openai_dependency.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            stream=True,
            max_tokens=10) # Ліміт відповіді
        
        generated_message = ""
        async for chunk in stream:
           if chunk.choices[0].delta.content is not None:
              generated_message += chunk.choices[0].delta.content
        print(f"Generated message: {generated_message}")

    except Exception as e:
        print(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500,
                            detail=f"Error generating response: {str(e)}")
    return {"generated_message": generated_message}