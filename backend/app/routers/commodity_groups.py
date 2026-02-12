from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import CommodityGroup

router = APIRouter(prefix="/commodity-groups", tags=["commodity-groups"])


@router.get("")
def list_commodity_groups(db: Session = Depends(get_db)):
    return db.query(CommodityGroup).order_by(CommodityGroup.id).all()
