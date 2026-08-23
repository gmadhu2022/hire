from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import hash_password, generate_password
from ..email_utils import send_credentials_email
from ..config import settings
from ..job_taxonomy import taxonomy_payload

router = APIRouter(prefix="/api/public", tags=["public"])


@router.post("/register/enterprise", response_model=schemas.CredentialResult)
def register_enterprise(body: schemas.EnterpriseRegister, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(400, "A user with this email already exists.")
    password = generate_password()
    user = models.User(email=body.email, password_hash=hash_password(password),
                       role=models.ROLE_ENTERPRISE, must_change_password=True)
    db.add(user)
    db.flush()
    ent = models.Enterprise(user_id=user.id, **body.model_dump())
    db.add(ent)
    db.commit()
    send_credentials_email(body.email, body.name, body.email, password)
    return schemas.CredentialResult(email=body.email, user_id=body.email, password=password,
                                    status="You have successfully registered as Employer")


@router.post("/register/jobseeker", response_model=schemas.CredentialResult)
def register_jobseeker(body: schemas.JobSeekerSelfRegister, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(400, "A user with this email already exists.")
    password = generate_password()
    user = models.User(email=body.email, password_hash=hash_password(password),
                       role=models.ROLE_JOBSEEKER, must_change_password=True)
    db.add(user)
    db.flush()

    # Per user story: voluntary registrations are attached to the default institute.
    default_inst = db.query(models.Institute).filter(
        models.Institute.name == settings.DEFAULT_INSTITUTE_NAME).first()

    data = body.model_dump()
    data["education"] = [e for e in (data.get("education") or [])]
    data["experience"] = [e for e in (data.get("experience") or [])]
    seeker = models.JobSeeker(user_id=user.id,
                              institute_id=default_inst.id if default_inst else None, **data)
    db.add(seeker)
    db.commit()
    name = f"{body.first_name or ''} {body.last_name or ''}".strip() or body.email
    send_credentials_email(body.email, name, body.email, password)
    return schemas.CredentialResult(email=body.email, user_id=body.email, password=password,
                                    status="You have successfully registered as Job Seeker")


@router.get("/taxonomy")
def taxonomy():
    """Every sector and role the platform covers — daily wage through postgraduate."""
    return taxonomy_payload()


@router.get("/banners")
def active_banners(audience: str = "jobseekers", db: Session = Depends(get_db)):
    """Active banners for an audience, highest priority first.

    Powers the global banner strip shown on every job-seeker page (item 4).
    Respects start/end dates when set.
    """
    from datetime import date
    today = date.today().isoformat()
    rows = (db.query(models.Banner)
            .filter(models.Banner.status == "active",
                    models.Banner.audience.in_([audience, "all"]))
            .order_by(models.Banner.priority.desc(), models.Banner.created_at.desc())
            .limit(10).all())
    out = []
    for b in rows:
        if b.start_date and str(b.start_date) > today:
            continue
        if b.end_date and str(b.end_date) < today:
            continue
        b.impressions = (b.impressions or 0) + 1
        out.append({
            "id": b.id, "title": b.title, "company_name": b.company_name,
            "text_content": b.text_content, "media_type": b.media_type,
            "media_url": b.media_url or b.image_url, "poster_url": b.poster_url,
            "cta_label": b.cta_label, "cta_link": b.cta_link, "theme": b.theme,
            "autoplay": b.autoplay, "muted": b.muted, "logo_url": b.logo_url,
        })
    db.commit()
    return out


@router.post("/banners/{banner_id}/click")
def banner_click(banner_id: int, db: Session = Depends(get_db)):
    b = db.query(models.Banner).get(banner_id)
    if b:
        b.clicks = (b.clicks or 0) + 1
        db.commit()
    return {"ok": True}


@router.get("/stats")
def public_stats(db: Session = Depends(get_db)):
    """Headline counts shown on the home page."""
    return {
        "jobs": db.query(models.Job).filter(models.Job.status == "active").count(),
        "jobseekers": db.query(models.JobSeeker).count(),
        "enterprises": db.query(models.Enterprise).count(),
        "institutes": db.query(models.Institute).count(),
    }


@router.get("/jobs")
def public_jobs(limit: int = 6, db: Session = Depends(get_db)):
    """A few latest jobs to showcase on the home page (no login required)."""
    rows = db.query(models.Job).filter(models.Job.status == "active").order_by(
        models.Job.created_at.desc()).limit(limit).all()
    return [{"id": j.id, "title": j.title, "location": j.location, "category": j.category,
             "experience": j.experience, "key_skills": j.key_skills} for j in rows]
