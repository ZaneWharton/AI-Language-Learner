from pydantic import BaseModel
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import json, openai
from openai import OpenAIError
from app.db import get_db
from app.models import User, Question, UserLanguageProgress
from app.routes.auth import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/placement-test", tags=["placement-test"])
openai.api_key = settings.OPENAI_API_KEY

#Question output schema
class QuestionOut(BaseModel):
    id: int
    prompt: str
    choices: List[str]
    correct_choice: str
    language: str
    class Config:
        orm_mode = True

#Placement test results input schema
class PlacementResult(BaseModel):
    language: str
    level: str

#Admin dependency
async def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user

#Generate test questions, admin access required
@router.get("/generate", response_model=List[QuestionOut])
async def generate_questions(language: str = Query("Spanish"), 
                       num_questions: int = Query(10, ge=1, le=50), 
                       db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(admin_required)):
    
    #OpenAI prompts
    system = f"You are an expert at generating quizes for {language} learners."
    user_prompt = (
        f"Generate {num_questions} multiple choice questions for learning {language} with the following difficulty distribution:\n"
        f"- 30% Beginner (basic vocabulary, common greetings, numbers 1-10, days of week)\n"
        f"- 40% Intermediate (grammar rules, verb conjugations, sentence structure, past/future tenses)\n"
        f"- 30% Advanced (subjunctive mood, complex grammar, idioms)\n\n"
        f"Question types should include:\n"
        f"- Vocabulary translation (both directions)\n"
        f"- Grammar/conjugation (choose correct verb form)\n"
        f"- Sentence completion (fill in missing word)\n"
        f"- Reading comprehension (short passages with questions)\n"
        f"Make incorrect choices plausible but clearly wrong to native speakers. "
        f"For advanced questions, use complex sentence structures and nuanced vocabulary.\n\n"
        f"Return ONLY a valid JSON array with no additional text or formatting. "
        f"Each object must have exactly these keys: "
        f'"prompt" (string for the question), '
        f'"choices" (array of exactly 4 strings), '
        f'"correct_choice" (string that exactly matches one of the choices). '
        f"Example format: "
        f'[{{"prompt": "What is hello in {language}?", "choices": ["hola", "adios", "gracias", "por favor"], "correct_choice": "hola"}}]'
    )
    
    #Attempt to retrieve response
    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user_prompt}
            ],
            temperature=0.2,
        )

        content = resp.choices[0].message.content.strip()

        #Clean response if has markdown formatting
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        questions = json.loads(content)

    except OpenAIError as e:
        raise HTTPException(502, detail=f"LLM API error: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error. Raw content: {content}")
        raise HTTPException(502, detail=f"Invalid JSON from LLM: {str(e)}")
    except Exception as e:
        raise HTTPException(502, detail=f"Unexpected error: {str(e)}")
    
    #Save the questions in db
    created = []
    for q in questions:
        #Validate shape
        if not (q.get("prompt") and isinstance(q.get("choices"), list) and len(q["choices"]) == 4 and q.get("correct_choice") in q.get("choices", [])):
            continue
        obj = Question(
            prompt=q["prompt"],
            choices=q["choices"],
            correct_choice=q["correct_choice"],
            language=language,
            )
        db.add(obj)
        created.append(obj)
    
    await db.commit()
    for obj in created:
        db.refresh(obj)
    
    if not created:
        raise HTTPException(500, "No valid questions generated")
    return created

#Returns 20 test questions
@router.get("/test", response_model=List[QuestionOut])
async def get_placement_test(language: str = Query("Spanish"), db: AsyncSession = Depends(get_db)):

    query = (
        select(Question)
        .where(Question.language == language)
        .order_by(func.random())
        .limit(20)
    )

    result = await db.execute(query)
    questions = result.scalars().all()

    return questions

#Saves placement test results into database
@router.post("/result")
async def submit_results(data: PlacementResult, 
                         db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    
    result = await db.execute(
        select(UserLanguageProgress).where(
            UserLanguageProgress.user_id == current_user.id,
            UserLanguageProgress.language == data.language
    ))

    #If the user has already made progress in the selected language it updates that laguage, if not a new row is added to db table
    progress = result.scalar_one_or_none()
    if progress:
        progress.level = data.level
    else:
        progress = UserLanguageProgress(
            user_id = current_user.id,
            language = data.language,
            level = data.level
        )
        db.add(progress)

    #Updates the current language the user is learning
    current_user.current_language = data.language

    await db.commit()
    return {"message": "Placement result saved.", "language": data.language, "level": data.level}
