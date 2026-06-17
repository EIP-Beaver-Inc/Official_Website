from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
import logging
import secrets
import string
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


def _generate_beta_key() -> str:
    chars = string.ascii_uppercase + string.digits
    parts = [''.join(secrets.choice(chars) for _ in range(4)) for _ in range(4)]
    return '-'.join(parts)


# ====================== Admin auth ======================
_admin_key_header = APIKeyHeader(name="X-Admin-Token", auto_error=False)


async def require_admin(token: str = Depends(_admin_key_header)):
    expected = os.environ.get("ADMIN_TOKEN", "")
    if not expected or token != expected:
        raise HTTPException(status_code=401, detail="Accès non autorisé.")


# ====================== Client auth dependency ======================
async def _get_client(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requis.")
    token = authorization[len("Bearer "):]
    c = await db.beta_clients.find_one({"session_token": token}, {"_id": 0})
    if not c:
        raise HTTPException(status_code=401, detail="Session invalide.")
    key_doc = await db.beta_keys.find_one({"key": c["key"]}, {"_id": 0})
    if key_doc and key_doc.get("status") == "revoked":
        raise HTTPException(status_code=403, detail="Accès révoqué.")
    return c


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


class AdminLogin(BaseModel):
    password: str


class BetaKeyGenerate(BaseModel):
    company: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None, max_length=500)
    expires_at: Optional[str] = None


class BetaKey(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str = Field(default_factory=_generate_beta_key)
    status: str = "unused"
    company: Optional[str] = None
    notes: Optional[str] = None
    created_at: str = Field(default_factory=_now_iso)
    expires_at: Optional[str] = None
    used_at: Optional[str] = None


class BetaValidate(BaseModel):
    key: str
    company: str = Field(min_length=1, max_length=200)
    contact_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=40)


class BetaLogin(BaseModel):
    key: str


class BetaClient(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str
    company: str
    contact_name: str
    email: str
    phone: Optional[str] = None
    registered_at: str = Field(default_factory=_now_iso)
    session_token: str = Field(default_factory=lambda: str(uuid.uuid4()))


TICKET_STATUSES = ["open", "in_progress", "resolved", "closed"]
TICKET_CATEGORIES = ["Bug", "Question", "Amélioration", "Autre"]
FEEDBACK_CATEGORIES = ["Interface", "Performance", "Précision IA", "Documentation", "Autre"]


class TicketMessageIn(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class TicketMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author: str  # "client" | "admin"
    content: str
    created_at: str = Field(default_factory=_now_iso)


class SatisfactionCreate(BaseModel):
    nps: int = Field(ge=0, le=10)
    csat: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=1000)


class TicketCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    category: str = Field(default="Autre")


class TicketDoc(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    company: str
    contact_name: str
    email: str
    subject: str
    description: str
    category: str
    status: str = "open"
    messages: List[dict] = []
    satisfaction: Optional[dict] = None
    unread_for_client: bool = False
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)


class FeedbackCreate(BaseModel):
    category: str = Field(default="Autre")
    content: str = Field(min_length=1, max_length=3000)


class FeedbackRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    company: str
    contact_name: str
    email: str
    category: str
    content: str
    created_at: str = Field(default_factory=_now_iso)


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


# ---- Tutorials ----
def _load_tutorials() -> list:
    tutorials_dir = ROOT_DIR / "tutorials"
    if not tutorials_dir.is_dir():
        return []
    items = []
    for f in sorted(tutorials_dir.glob("*.json")):
        try:
            import json
            items.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass
    return sorted(items, key=lambda t: t.get("order", 999))


@api_router.get("/beta/tutorials")
async def get_tutorials():
    return {"tutorials": _load_tutorials()}


# ---- Beta access ----
@api_router.post("/beta/validate")
async def validate_beta_key(payload: BetaValidate):
    normalized = payload.key.strip().upper()
    doc = await db.beta_keys.find_one({"key": normalized}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Clé invalide.")
    if doc["status"] == "active":
        raise HTTPException(status_code=409, detail="Cette clé a déjà été utilisée.")
    if doc["status"] == "expired":
        raise HTTPException(status_code=410, detail="Cette clé est expirée.")
    if doc["status"] == "revoked":
        raise HTTPException(status_code=403, detail="Cette clé a été révoquée. Contactez Beaver.")
    if doc.get("expires_at"):
        exp = datetime.fromisoformat(doc["expires_at"])
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > exp:
            await db.beta_keys.update_one({"key": normalized}, {"$set": {"status": "expired"}})
            raise HTTPException(status_code=410, detail="Cette clé est expirée.")

    client = BetaClient(
        key=normalized,
        company=payload.company,
        contact_name=payload.contact_name,
        email=payload.email,
        phone=payload.phone,
    )
    await db.beta_clients.insert_one(client.model_dump())
    await db.beta_keys.update_one(
        {"key": normalized},
        {"$set": {"status": "active", "used_at": _now_iso()}},
    )
    return {"success": True, "session_token": client.session_token, "client_id": client.id}


@api_router.post("/beta/login")
async def beta_login(payload: BetaLogin):
    normalized = payload.key.strip().upper()
    key_doc = await db.beta_keys.find_one({"key": normalized}, {"_id": 0})
    if not key_doc:
        raise HTTPException(status_code=404, detail="Clé invalide.")
    if key_doc["status"] == "unused":
        raise HTTPException(status_code=400, detail="Clé non encore activée. Créez d'abord votre compte.")
    if key_doc["status"] == "expired":
        raise HTTPException(status_code=410, detail="Cette clé est expirée.")
    if key_doc["status"] == "revoked":
        raise HTTPException(status_code=403, detail="Cette clé a été révoquée. Contactez Beaver.")
    c = await db.beta_clients.find_one({"key": normalized}, {"_id": 0})
    if not c:
        raise HTTPException(status_code=404, detail="Compte introuvable.")
    new_token = str(uuid.uuid4())
    await db.beta_clients.update_one({"key": normalized}, {"$set": {"session_token": new_token}})
    return {"success": True, "session_token": new_token, "client_id": c["id"]}


@api_router.get("/beta/me")
async def get_beta_me(c: dict = Depends(_get_client)):
    key_doc = await db.beta_keys.find_one({"key": c["key"]}, {"_id": 0})
    return {
        "client_id": c["id"],
        "company": c["company"],
        "contact_name": c["contact_name"],
        "email": c["email"],
        "registered_at": c["registered_at"],
        "key": c["key"],
        "expires_at": key_doc.get("expires_at") if key_doc else None,
    }


# ---- Tickets (client) ----
@api_router.post("/beta/tickets")
async def create_ticket(payload: TicketCreate, c: dict = Depends(_get_client)):
    if payload.category not in TICKET_CATEGORIES:
        payload.category = "Autre"
    ticket = TicketDoc(
        client_id=c["id"], company=c["company"],
        contact_name=c["contact_name"], email=c["email"],
        subject=payload.subject, description=payload.description, category=payload.category,
    )
    await db.tickets.insert_one(ticket.model_dump())
    doc = ticket.model_dump()
    doc.pop("_id", None)
    return doc


@api_router.get("/beta/tickets")
async def list_my_tickets(c: dict = Depends(_get_client)):
    cursor = db.tickets.find({"client_id": c["id"]}, {"_id": 0}).sort("updated_at", -1)
    tickets = await cursor.to_list(length=200)
    unread_count = sum(1 for t in tickets if t.get("unread_for_client"))
    return {"tickets": tickets, "unread_count": unread_count}


@api_router.get("/beta/tickets/{ticket_id}")
async def get_ticket(ticket_id: str, c: dict = Depends(_get_client)):
    ticket = await db.tickets.find_one({"id": ticket_id, "client_id": c["id"]}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")
    return ticket


@api_router.post("/beta/tickets/{ticket_id}/seen")
async def mark_ticket_seen(ticket_id: str, c: dict = Depends(_get_client)):
    result = await db.tickets.update_one(
        {"id": ticket_id, "client_id": c["id"]},
        {"$set": {"unread_for_client": False}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")
    return {"success": True}


@api_router.post("/beta/tickets/{ticket_id}/messages")
async def client_add_message(ticket_id: str, payload: TicketMessageIn, c: dict = Depends(_get_client)):
    ticket = await db.tickets.find_one({"id": ticket_id, "client_id": c["id"]}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")
    if ticket["status"] == "closed":
        raise HTTPException(status_code=400, detail="Ce ticket est fermé.")
    msg = TicketMessage(author="client", content=payload.content)
    await db.tickets.update_one(
        {"id": ticket_id},
        {"$push": {"messages": msg.model_dump()},
         "$set": {"updated_at": _now_iso(), "unread_for_client": False}},
    )
    return msg.model_dump()


@api_router.post("/beta/tickets/{ticket_id}/satisfaction")
async def submit_satisfaction(ticket_id: str, payload: SatisfactionCreate, c: dict = Depends(_get_client)):
    ticket = await db.tickets.find_one({"id": ticket_id, "client_id": c["id"]}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")
    if ticket["status"] != "resolved":
        raise HTTPException(status_code=400, detail="Le ticket doit être résolu pour évaluer.")
    if ticket.get("satisfaction"):
        raise HTTPException(status_code=409, detail="Satisfaction déjà soumise.")
    sat = {**payload.model_dump(), "submitted_at": _now_iso()}
    await db.tickets.update_one(
        {"id": ticket_id},
        {"$set": {"satisfaction": sat, "status": "closed", "updated_at": _now_iso()}},
    )
    return {"success": True}


# ---- Feedback (client) ----
@api_router.post("/beta/feedback")
async def submit_feedback(payload: FeedbackCreate, c: dict = Depends(_get_client)):
    if payload.category not in FEEDBACK_CATEGORIES:
        payload.category = "Autre"
    fb = FeedbackRecord(
        client_id=c["id"], company=c["company"],
        contact_name=c["contact_name"], email=c["email"],
        category=payload.category, content=payload.content,
    )
    await db.feedback.insert_one(fb.model_dump())
    return {"success": True}


# ---- Tickets (admin) ----
@api_router.get("/admin/tickets", dependencies=[Depends(require_admin)])
async def admin_list_tickets(status: Optional[str] = None, limit: int = 200):
    query = {"status": status} if status else {}
    cursor = db.tickets.find(query, {"_id": 0}).sort("updated_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


class AdminTicketUpdate(BaseModel):
    status: str


@api_router.patch("/admin/tickets/{ticket_id}", dependencies=[Depends(require_admin)])
async def admin_update_ticket(ticket_id: str, payload: AdminTicketUpdate):
    if payload.status not in TICKET_STATUSES:
        raise HTTPException(status_code=400, detail="Statut invalide.")
    result = await db.tickets.update_one(
        {"id": ticket_id},
        {"$set": {"status": payload.status, "updated_at": _now_iso(), "unread_for_client": True}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")
    return {"success": True}


@api_router.post("/admin/tickets/{ticket_id}/messages", dependencies=[Depends(require_admin)])
async def admin_reply_ticket(ticket_id: str, payload: TicketMessageIn):
    ticket = await db.tickets.find_one({"id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")
    msg = TicketMessage(author="admin", content=payload.content)
    await db.tickets.update_one(
        {"id": ticket_id},
        {"$push": {"messages": msg.model_dump()},
         "$set": {"updated_at": _now_iso(), "unread_for_client": True}},
    )
    return msg.model_dump()


# ---- Feedback (admin) ----
@api_router.get("/admin/feedback", dependencies=[Depends(require_admin)])
async def admin_list_feedback(limit: int = 200):
    cursor = db.feedback.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


# ---- Stats (admin) ----
@api_router.get("/admin/stats", dependencies=[Depends(require_admin)])
async def admin_stats():
    all_tickets = await db.tickets.find({}, {"_id": 0}).to_list(length=2000)
    all_feedback = await db.feedback.find({}, {"_id": 0}).to_list(length=2000)
    all_clients = await db.beta_clients.find({}, {"_id": 0}).to_list(length=2000)
    all_keys = await db.beta_keys.find({}, {"_id": 0}).to_list(length=2000)

    satisfactions = [t["satisfaction"] for t in all_tickets if t.get("satisfaction")]
    nps_scores = [s["nps"] for s in satisfactions]
    csat_scores = [s["csat"] for s in satisfactions]

    nps_avg = round(sum(nps_scores) / len(nps_scores), 1) if nps_scores else None
    csat_avg = round(sum(csat_scores) / len(csat_scores), 2) if csat_scores else None

    promoters = sum(1 for s in nps_scores if s >= 9)
    passives = sum(1 for s in nps_scores if 7 <= s <= 8)
    detractors = sum(1 for s in nps_scores if s <= 6)
    nps_score = round((promoters - detractors) / len(nps_scores) * 100) if nps_scores else None

    ticket_by_status = {s: sum(1 for t in all_tickets if t["status"] == s) for s in TICKET_STATUSES}
    ticket_by_category: dict = {}
    for t in all_tickets:
        cat = t.get("category", "Autre")
        ticket_by_category[cat] = ticket_by_category.get(cat, 0) + 1

    feedback_by_category: dict = {}
    for f in all_feedback:
        cat = f.get("category", "Autre")
        feedback_by_category[cat] = feedback_by_category.get(cat, 0) + 1

    total_keys = len(all_keys)
    active_keys = sum(1 for k in all_keys if k["status"] == "active")
    conversion_rate = round(active_keys / total_keys * 100, 1) if total_keys else 0

    comments = [
        {
            "company": t["company"],
            "contact_name": t["contact_name"],
            "nps": t["satisfaction"]["nps"],
            "csat": t["satisfaction"]["csat"],
            "comment": t["satisfaction"].get("comment"),
            "submitted_at": t["satisfaction"].get("submitted_at"),
        }
        for t in all_tickets
        if t.get("satisfaction") and t["satisfaction"].get("comment")
    ]
    comments.sort(key=lambda x: x.get("submitted_at") or "", reverse=True)

    return {
        "nps_score": nps_score,
        "nps_avg": nps_avg,
        "csat_avg": csat_avg,
        "satisfaction_count": len(satisfactions),
        "nps_distribution": {"promoters": promoters, "passives": passives, "detractors": detractors},
        "ticket_count": len(all_tickets),
        "ticket_by_status": ticket_by_status,
        "ticket_by_category": ticket_by_category,
        "feedback_count": len(all_feedback),
        "feedback_by_category": feedback_by_category,
        "client_count": len(all_clients),
        "key_conversion_rate": conversion_rate,
        "satisfaction_comments": comments,
    }


# ---- Admin ----
@api_router.post("/admin/login")
async def admin_login(payload: AdminLogin):
    expected = os.environ.get("ADMIN_TOKEN", "")
    if not expected or payload.password != expected:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect.")
    return {"success": True, "token": expected}


@api_router.post("/admin/beta/generate", dependencies=[Depends(require_admin)])
async def generate_beta_key_endpoint(payload: BetaKeyGenerate):
    beta_key = BetaKey(company=payload.company, notes=payload.notes, expires_at=payload.expires_at)
    await db.beta_keys.insert_one(beta_key.model_dump())
    doc = beta_key.model_dump()
    doc.pop("_id", None)
    return doc


@api_router.get("/admin/beta/keys", dependencies=[Depends(require_admin)])
async def list_beta_keys(limit: int = 200):
    cursor = db.beta_keys.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


@api_router.get("/admin/beta/clients", dependencies=[Depends(require_admin)])
async def list_beta_clients(limit: int = 200):
    cursor = db.beta_clients.find({}, {"_id": 0}).sort("registered_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


@api_router.delete("/admin/beta/clients/{client_id}", dependencies=[Depends(require_admin)])
async def delete_beta_client(client_id: str):
    client = await db.beta_clients.find_one({"id": client_id}, {"_id": 0})
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable.")
    await db.beta_keys.update_one(
        {"key": client["key"]},
        {"$set": {"status": "revoked", "used_at": None}},
    )
    await db.beta_clients.delete_one({"id": client_id})
    return {"success": True}


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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)


