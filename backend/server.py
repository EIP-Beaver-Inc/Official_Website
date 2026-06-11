from fastapi import FastAPI, APIRouter, HTTPException
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from quiz_data import QUIZ_QUESTIONS, build_public_questions, evaluate_answers, get_answer_groups
from defects_data import DEFECT_CLASSES, PIPELINE_STEPS, SCORING_CLASSES, PRODUCT_TYPES, QUALITY_CLASSES

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    client.close()

app = FastAPI(title="BEAVER Marketing API", version="1.0.0", lifespan=lifespan)
api_router = APIRouter(prefix="/api")


# ====================== Helpers ======================
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _doc_to_public(doc: dict) -> dict:
    if not doc:
        return doc
    doc.pop('_id', None)
    return doc


# ====================== Models ======================
class DemoRequestCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=120)
    entreprise: str = Field(min_length=1, max_length=160)
    email: EmailStr
    telephone: Optional[str] = Field(default=None, max_length=40)
    taille_scierie: Optional[str] = Field(default=None, max_length=80)
    volume: Optional[str] = Field(default=None, max_length=80)
    message: Optional[str] = Field(default=None, max_length=2000)


class DemoRequest(DemoRequestCreate):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=_now_iso)


class ContactCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=120)
    entreprise: Optional[str] = Field(default=None, max_length=160)
    email: EmailStr
    telephone: Optional[str] = Field(default=None, max_length=40)
    message: str = Field(min_length=1, max_length=4000)


class Contact(ContactCreate):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=_now_iso)


class QuizAnswer(BaseModel):
    question_id: str
    selected: str  # option key (e.g. 'a', 'b', 'c', 'd')


class QuizSubmission(BaseModel):
    answers: List[QuizAnswer]
    email: Optional[EmailStr] = None
    nom: Optional[str] = Field(default=None, max_length=120)
    entreprise: Optional[str] = Field(default=None, max_length=160)


class QuizResultDetail(BaseModel):
    question_id: str
    image_url: Optional[str] = None
    product_type: Optional[str] = None
    selected: Optional[str] = None
    selected_code: Optional[str] = None
    correct: str
    correct_code: Optional[str] = None
    is_correct: bool
    explanation: str


class QuizResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    score: int
    total: int
    percentage: float
    details: List[QuizResultDetail]
    completed_at: str = Field(default_factory=_now_iso)
    email: Optional[str] = None
    nom: Optional[str] = None
    entreprise: Optional[str] = None


# ====================== Routes ======================
@api_router.get("/")
async def root():
    return {"name": "BEAVER Marketing API", "status": "ok"}


@api_router.get("/health")
async def health():
    try:
        await db.command("ping")
        return {"status": "healthy", "mongo": "connected"}
    except Exception as e:  # pragma: no cover
        return {"status": "degraded", "mongo": "error", "error": str(e)}


# ---- Pipeline / Defects info ----
@api_router.get("/pipeline")
async def get_pipeline_info():
    return {
        "steps": PIPELINE_STEPS,
        "defect_classes": DEFECT_CLASSES,
        "scoring_classes": SCORING_CLASSES,
    }


@api_router.get("/defects")
async def get_defects():
    return {"defects": DEFECT_CLASSES}


@api_router.get("/scoring")
async def get_scoring():
    return {"classes": SCORING_CLASSES}


# ---- Quiz ----
@api_router.get("/quiz/questions")
async def get_quiz_questions():
    return {
        "product_types": PRODUCT_TYPES,
        "quality_classes": QUALITY_CLASSES,
        "answer_groups": get_answer_groups(),
        "questions": build_public_questions(),
        "total": len(QUIZ_QUESTIONS),
    }


@api_router.post("/quiz/submit", response_model=QuizResult)
async def submit_quiz(payload: QuizSubmission):
    if not payload.answers:
        raise HTTPException(status_code=400, detail="Aucune réponse fournie.")

    score, total, details_raw = evaluate_answers([a.model_dump() for a in payload.answers])
    percentage = round((score / total) * 100, 1) if total else 0.0

    details = [QuizResultDetail(**d) for d in details_raw]

    result = QuizResult(
        score=score,
        total=total,
        percentage=percentage,
        details=details,
        email=payload.email,
        nom=payload.nom,
        entreprise=payload.entreprise,
    )

    doc = result.model_dump()
    await db.quiz_results.insert_one(doc)
    return result


@api_router.get("/quiz/results", response_model=List[QuizResult])
async def list_quiz_results(limit: int = 100):
    cursor = db.quiz_results.find({}, {"_id": 0}).sort("completed_at", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    return items


# ---- Demo requests ----
@api_router.post("/demo-requests", response_model=DemoRequest)
async def create_demo_request(payload: DemoRequestCreate):
    obj = DemoRequest(**payload.model_dump())
    await db.demo_requests.insert_one(obj.model_dump())
    return obj


@api_router.get("/demo-requests", response_model=List[DemoRequest])
async def list_demo_requests(limit: int = 200):
    cursor = db.demo_requests.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    return items


# ---- Contacts ----
@api_router.post("/contact", response_model=Contact)
async def create_contact(payload: ContactCreate):
    obj = Contact(**payload.model_dump())
    await db.contacts.insert_one(obj.model_dump())
    return obj


@api_router.get("/contact", response_model=List[Contact])
async def list_contacts(limit: int = 200):
    cursor = db.contacts.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    return items


# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


