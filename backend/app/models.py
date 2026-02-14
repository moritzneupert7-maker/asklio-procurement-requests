from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship

from .db import Base


class CommodityGroup(Base):
    __tablename__ = "commodity_groups"

    id = Column(String(3), primary_key=True)  # "001"..."050"
    category = Column(String(100), nullable=False)
    name = Column(String(150), nullable=False)


class ProcurementRequest(Base):
    __tablename__ = "procurement_requests"

    id = Column(Integer, primary_key=True, index=True)

    requestor_name = Column(String(200), nullable=False)
    title = Column(String(250), nullable=False)
    department = Column(String(200), nullable=False)

    vendor_name = Column(String(250), nullable=False)
    vendor_vat_id = Column(String(50), nullable=True)

    commodity_group_id = Column(String(3), ForeignKey("commodity_groups.id"), nullable=True)

    total_cost = Column(Numeric(12, 2), nullable=False, default=0)
    current_status = Column(String(30), nullable=False, default="Open")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    commodity_group = relationship("CommodityGroup")
    order_lines = relationship("OrderLine", back_populates="request", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="request", cascade="all, delete-orphan")
    status_events = relationship("StatusEvent", back_populates="request", cascade="all, delete-orphan")


class OrderLine(Base):
    __tablename__ = "order_lines"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("procurement_requests.id"), nullable=False, index=True)

    product = Column(String(250), nullable=True)
    description = Column(String(500), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    amount = Column(Integer, nullable=False)
    unit = Column(String(50), nullable=True)
    total_price = Column(Numeric(12, 2), nullable=False)

    request = relationship("ProcurementRequest", back_populates="order_lines")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("procurement_requests.id"), nullable=False, index=True)

    filename = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    request = relationship("ProcurementRequest", back_populates="attachments")


class StatusEvent(Base):
    __tablename__ = "status_events"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("procurement_requests.id"), nullable=False, index=True)

    from_status = Column(String(30), nullable=True)
    to_status = Column(String(30), nullable=False)

    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    changed_by = Column(String(200), nullable=True)

    request = relationship("ProcurementRequest", back_populates="status_events")
