import os
from pathlib import Path
import pdfplumber 

from ..models import CommodityGroup

from fastapi import File, UploadFile

from ..services.extractor import extract_offer_text
from ..services.commodity import predict_commodity_group_id


from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/requests", tags=["requests"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("", response_model=schemas.ProcurementRequestOut)
def create_request(payload: schemas.ProcurementRequestCreate, db: Session = Depends(get_db)):
    req = models.ProcurementRequest(
        requestor_name=payload.requestor_name,
        title=payload.title,
        department=payload.department,
        vendor_name=payload.vendor_name,
        vendor_vat_id=payload.vendor_vat_id,
        commodity_group_id=None,
        current_status="Open",
        total_cost=Decimal("0.00"),
    )

    total_cost = Decimal("0.00")
    for line in payload.order_lines:
        line_total = (line.unit_price * Decimal(line.amount)).quantize(Decimal("0.01"))
        total_cost += line_total
        req.order_lines.append(
            models.OrderLine(
                product=line.product,
                description=line.description,
                unit_price=line.unit_price,
                amount=line.amount,
                unit=line.unit,
                total_price=line_total,
            )
        )

    req.total_cost = total_cost.quantize(Decimal("0.01"))

    # status history (immutable events)
    req.status_events.append(
        models.StatusEvent(from_status=None, to_status="Open", changed_by=payload.requestor_name)
    )

    db.add(req)
    db.commit()
    db.refresh(req)
    return req




@router.post("/{request_id}/upload-offer")
async def upload_offer(request_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    req = db.get(models.ProcurementRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    contents = await file.read()
    safe_name = f"{request_id}_{file.filename}".replace("/", "_").replace("\\", "_")
    save_path = UPLOAD_DIR / safe_name
    save_path.write_bytes(contents)

    att = models.Attachment(
        request_id=request_id,
        filename=file.filename or safe_name,
        path=str(save_path),
    )
    db.add(att)
    db.commit()
    db.refresh(att)

    return {"attachment_id": att.id, "filename": att.filename}



@router.get("", response_model=list[schemas.ProcurementRequestOut])
def list_requests(db: Session = Depends(get_db)):
    return db.query(models.ProcurementRequest).order_by(models.ProcurementRequest.id.desc()).all()


@router.get("/{request_id}", response_model=schemas.ProcurementRequestOut)
def get_request(request_id: int, db: Session = Depends(get_db)):
    req = db.get(models.ProcurementRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req

@router.post("/{request_id}/extract-offer", response_model=schemas.ProcurementRequestOut)
def extract_offer(request_id: int, db: Session = Depends(get_db)):
    req = db.get(models.ProcurementRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    # Get latest attachment
    att = (
        db.query(models.Attachment)
        .filter(models.Attachment.request_id == request_id)
        .order_by(models.Attachment.id.desc())
        .first()
    )
    if not att:
        raise HTTPException(status_code=400, detail="No offer uploaded yet")

    path = Path(att.path)
    if not path.exists():
        raise HTTPException(status_code=500, detail="Uploaded file not found on server")

    # Read offer text from file (.txt or text-based .pdf)
    suffix = path.suffix.lower()

    if suffix == ".txt":
        offer_text = path.read_text(encoding="utf-8", errors="ignore")

    elif suffix == ".pdf":
        text_parts = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(page_text)
        offer_text = "\n\n".join(text_parts).strip()

        if not offer_text:
            raise HTTPException(
                status_code=400,
                detail="PDF has no extractable text (maybe scanned). Upload a text-based PDF or add OCR.",
            )
    else:
        raise HTTPException(status_code=400, detail="Supported offer types: .txt, .pdf")

    # LLM extraction
    try:
        extracted = extract_offer_text(offer_text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Extraction failed: {e}")

    # Apply extracted fields
    req.vendor_name = extracted.vendor_name
    req.vendor_vat_id = extracted.vendor_vat_id
    if extracted.department:
        req.department = extracted.department

    # Replace order lines + totals
    req.order_lines.clear()
    total_cost = Decimal("0.00")
    for line in extracted.order_lines:
        req.order_lines.append(
            models.OrderLine(
                product=line.product,
                description=line.description,
                unit_price=line.unit_price,
                amount=line.amount,
                unit=line.unit,
                total_price=line.total_price,
            )
        )
        total_cost += line.total_price
    req.total_cost = total_cost.quantize(Decimal("0.01"))

    # Predict commodity group (auto-fill)
    groups = db.query(models.CommodityGroup).order_by(models.CommodityGroup.id).all()
    groups_text = "\n".join([f"{g.id} | {g.category} | {g.name}" for g in groups])
    lines_text = "; ".join([ol.description for ol in req.order_lines])

    try:
        predicted = predict_commodity_group_id(
            title=req.title,
            department=req.department,
            vendor_name=req.vendor_name,
            order_lines_text=lines_text,
            commodity_groups_text=groups_text,
        )
        if db.get(models.CommodityGroup, predicted):
            req.commodity_group_id = predicted
    except Exception:
        pass  # keep request usable even if prediction fails

    db.add(req)
    db.commit()
    db.refresh(req)
    return req




@router.post("/{request_id}/status", response_model=schemas.ProcurementRequestOut)
def change_status(request_id: int, payload: schemas.StatusChange, db: Session = Depends(get_db)):
    req = db.get(models.ProcurementRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    from_status = req.current_status
    req.current_status = payload.to_status
    req.status_events.append(
        models.StatusEvent(from_status=from_status, to_status=payload.to_status, changed_by=payload.changed_by)
    )

    db.add(req)
    db.commit()
    db.refresh(req)
    return req

@router.post("/{request_id}/commodity-group", response_model=schemas.ProcurementRequestOut)
def set_commodity_group(request_id: int, payload: schemas.CommodityGroupSet, db: Session = Depends(get_db)):
    req = db.get(models.ProcurementRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    cg = db.get(CommodityGroup, payload.commodity_group_id)
    if not cg:
        raise HTTPException(status_code=400, detail="Invalid commodity_group_id")

    req.commodity_group_id = payload.commodity_group_id
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

