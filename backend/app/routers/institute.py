import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import require_role, get_current_user
from ..resume_service import process_institute_upload, sample_template_dataframe
from ..notify_service import notify_job_alert

router = APIRouter(prefix="/api/institute", tags=["institute"],
                   dependencies=[Depends(require_role(models.ROLE_INSTITUTE))])


def _institute(current: models.User, db: Session) -> models.Institute:
    inst = db.query(models.Institute).filter(models.Institute.user_id == current.id).first()
    if not inst:
        raise HTTPException(404, "Institute profile not found.")
    return inst


# ---------------- Profile ----------------
@router.get("/profile", response_model=schemas.InstituteOut)
def get_profile(current: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _institute(current, db)


@router.put("/profile", response_model=schemas.InstituteOut)
def update_profile(body: schemas.InstituteBase,
                   current: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    inst = _institute(current, db)
    for k, v in body.model_dump(exclude={"email"}).items():
        setattr(inst, k, v)
    db.commit()
    db.refresh(inst)
    return inst


# ---------------- Data upload (THE emphasized flow) ----------------
@router.get("/upload-template")
def download_upload_template():
    """Download a blank .xlsx the institute can fill in and upload."""
    df = sample_template_dataframe()
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=hire_student_upload_template.xlsx"},
    )


@router.post("/upload")
async def upload_students(file: UploadFile = File(...),
                          current: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Upload an Excel of 1..N students. For each row we auto-create a resume,
    generate credentials, store in DB, and email the student their user id + password."""
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Please upload an .xlsx or .xls file.")
    inst = _institute(current, db)
    contents = await file.read()
    try:
        results = process_institute_upload(contents, inst, db)
    except Exception as e:
        raise HTTPException(400, f"Could not read the spreadsheet: {e}")

    created = sum(1 for r in results if r["status"].startswith("created"))
    return {
        "message": f"Successfully uploaded the data. {created} student account(s) created.",
        "results": results,
    }


# ---------------- Student search ----------------
@router.get("/students", response_model=list[schemas.JobSeekerOut])
def student_search(email: str | None = None, phone: str | None = None,
                   current: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Search this institute's students by email or phone (per user story)."""
    inst = _institute(current, db)
    query = db.query(models.JobSeeker).filter(models.JobSeeker.institute_id == inst.id)
    if email:
        query = query.filter(models.JobSeeker.email.ilike(f"%{email}%"))
    if phone:
        query = query.filter(models.JobSeeker.phone.ilike(f"%{phone}%"))
    return query.order_by(models.JobSeeker.created_at.desc()).all()


@router.get("/students/{jobseeker_id}", response_model=schemas.JobSeekerOut)
def view_student(jobseeker_id: int, current: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    inst = _institute(current, db)
    s = db.query(models.JobSeeker).filter_by(id=jobseeker_id, institute_id=inst.id).first()
    if not s:
        raise HTTPException(404, "Student not found in your institute.")
    return s


# ---------------- Post a job (institutes can post too) ----------------
@router.post("/jobs", response_model=schemas.JobOut)
def post_job(body: schemas.JobBase, current: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    inst = _institute(current, db)
    job = models.Job(institute_id=inst.id, posted_by_user_id=current.id, **body.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    notify_job_alert(db, job)
    return job
