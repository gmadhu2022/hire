"""AI endpoints (Groq). Every route returns 503 with a readable message when AI is off."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..auth import get_current_user, require_role
from .. import ai_service as ai
from ..notify_service import match_score

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _guard(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except ai.AIUnavailable as e:
        raise HTTPException(503, str(e))


def _seeker_dict(s: models.JobSeeker) -> dict:
    return {
        "name": f"{s.first_name or ''} {s.last_name or ''}".strip(),
        "location": s.location, "objective": s.career_objective,
        "skills": s.key_skills or [], "education": s.education or [],
        "experience": s.experience or [], "certifications": s.certifications or [],
        "languages": s.languages or [], "additional_info": s.additional_info,
    }


def _job_dict(j: models.Job) -> dict:
    return {
        "title": j.title, "location": j.location, "category": j.category,
        "description": j.description, "education": j.requirement_education,
        "technical": j.requirement_technical, "experience": j.experience,
        "salary": j.salary, "skills": j.key_skills or [],
    }


def _my_seeker(current: models.User, db: Session) -> models.JobSeeker:
    s = db.query(models.JobSeeker).filter_by(user_id=current.id).first()
    if not s:
        raise HTTPException(404, "Job seeker profile not found.")
    return s


@router.get("/models")
def list_available_models(current: models.User = Depends(get_current_user)):
    """List the model IDs this Groq key can use, so you can pick a valid GROQ_MODEL."""
    try:
        available = ai.list_models()
    except ai.AIUnavailable as e:
        raise HTTPException(503, str(e))
    return {
        "configured": ai.settings.GROQ_MODEL,
        "configured_is_valid": ai.settings.GROQ_MODEL in available,
        "available": available,
    }


@router.get("/status")
def status():
    """Lets the UI hide AI buttons when AI isn't configured."""
    return {"enabled": ai.ai_enabled(), "model": ai.settings.GROQ_MODEL if ai.ai_enabled() else None}


# ---------------- job seeker ----------------
@router.post("/resume/objective")
def ai_objective(current: models.User = Depends(require_role(models.ROLE_JOBSEEKER)),
                 db: Session = Depends(get_db)):
    return _guard(ai.improve_objective, _seeker_dict(_my_seeker(current, db)))


@router.post("/resume/skills")
def ai_skills(current: models.User = Depends(require_role(models.ROLE_JOBSEEKER)),
              db: Session = Depends(get_db)):
    return _guard(ai.suggest_skills, _seeker_dict(_my_seeker(current, db)))


@router.post("/resume/parse")
def ai_parse_resume(body: dict, current: models.User = Depends(require_role(models.ROLE_JOBSEEKER))):
    text = (body.get("text") or "").strip()
    if len(text) < 40:
        raise HTTPException(400, "Paste a bit more of your resume text (at least 40 characters).")
    return _guard(ai.parse_resume_text, text)


@router.post("/jobs/{job_id}/explain")
def ai_explain(job_id: int, current: models.User = Depends(require_role(models.ROLE_JOBSEEKER)),
               db: Session = Depends(get_db)):
    seeker = _my_seeker(current, db)
    job = db.query(models.Job).get(job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    score, matched = match_score(seeker, job)
    return _guard(ai.explain_match, _seeker_dict(seeker), _job_dict(job), score, matched)


@router.post("/jobs/{job_id}/interview-prep")
def ai_interview(job_id: int, current: models.User = Depends(require_role(models.ROLE_JOBSEEKER)),
                 db: Session = Depends(get_db)):
    seeker = _my_seeker(current, db)
    job = db.query(models.Job).get(job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    return _guard(ai.interview_prep, _seeker_dict(seeker), _job_dict(job))


@router.post("/jobs/{job_id}/cover-letter")
def ai_cover_letter(job_id: int, current: models.User = Depends(require_role(models.ROLE_JOBSEEKER)),
                    db: Session = Depends(get_db)):
    seeker = _my_seeker(current, db)
    job = db.query(models.Job).get(job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    return _guard(ai.cover_letter, _seeker_dict(seeker), _job_dict(job))


# ---------------- recruiter ----------------
@router.post("/job/describe")
def ai_job_description(body: dict, current: models.User = Depends(get_current_user)):
    if current.role not in (models.ROLE_ENTERPRISE, models.ROLE_INSTITUTE):
        raise HTTPException(403, "Only recruiters and institutes can generate job descriptions.")
    if not (body.get("title") or "").strip():
        raise HTTPException(400, "Enter a job title first.")
    return _guard(ai.generate_job_description, body)


@router.post("/candidate/{jobseeker_id}/summary")
def ai_candidate_summary(jobseeker_id: int, body: dict | None = None,
                         current: models.User = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if current.role not in (models.ROLE_ENTERPRISE, models.ROLE_INSTITUTE):
        raise HTTPException(403, "Only recruiters and institutes can summarise candidates.")
    s = db.query(models.JobSeeker).get(jobseeker_id)
    if not s:
        raise HTTPException(404, "Candidate not found.")
    job = None
    if body and body.get("job_id"):
        j = db.query(models.Job).get(body["job_id"])
        job = _job_dict(j) if j else None
    return _guard(ai.candidate_summary, _seeker_dict(s), job)


@router.post("/job/parse")
def ai_parse_jd(body: dict, current: models.User = Depends(get_current_user)):
    """Paste a job description -> structured fields to auto-populate the post-job form."""
    if current.role not in (models.ROLE_ENTERPRISE, models.ROLE_INSTITUTE):
        raise HTTPException(403, "Only recruiters and institutes can post jobs.")
    text = (body.get("text") or "").strip()
    if len(text) < 40:
        raise HTTPException(400, "Paste a bit more of the job description (at least 40 characters).")
    return _guard(ai.parse_job_description, text)


@router.post("/job/classify")
def ai_classify(body: dict, current: models.User = Depends(get_current_user)):
    """Job title -> sector, education level, wage basis, suggested skills."""
    if current.role not in (models.ROLE_ENTERPRISE, models.ROLE_INSTITUTE):
        raise HTTPException(403, "Only recruiters and institutes can post jobs.")
    title = (body.get("title") or "").strip()
    if not title:
        raise HTTPException(400, "Enter a job title first.")
    from ..job_taxonomy import SECTORS
    return _guard(ai.classify_role, title, SECTORS)


@router.post("/banner/copy")
def ai_banner_copy(body: dict, current: models.User = Depends(get_current_user)):
    if current.role not in (models.ROLE_ENTERPRISE, models.ROLE_INSTITUTE, models.ROLE_ADMIN):
        raise HTTPException(403, "Not available for this account type.")
    return _guard(ai.banner_copy, body)


# ---------------- shared ----------------
@router.post("/resume/review")
def ai_resume_review(current: models.User = Depends(require_role(models.ROLE_JOBSEEKER)),
                     db: Session = Depends(get_db)):
    return _guard(ai.resume_review, _seeker_dict(_my_seeker(current, db)))


@router.post("/career/advice")
def ai_career_advice(current: models.User = Depends(require_role(models.ROLE_JOBSEEKER)),
                     db: Session = Depends(get_db)):
    return _guard(ai.career_advice, _seeker_dict(_my_seeker(current, db)))


@router.post("/search/parse")
def ai_search(body: dict, current: models.User = Depends(get_current_user)):
    q = (body.get("query") or "").strip()
    if not q:
        raise HTTPException(400, "Type what you're looking for.")
    return _guard(ai.parse_search, q)


@router.post("/suggest")
def ai_suggest(body: dict, current: models.User = Depends(get_current_user)):
    field = (body.get("field") or "").strip()
    if not field:
        raise HTTPException(400, "Field is required.")
    return _guard(ai.suggest_options, field, body.get("context", ""))
