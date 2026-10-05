import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CollectionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    SCHEDULED = "scheduled"
    COLLECTED = "collected"
    COMPLETED = "completed"
    REJECTED = "rejected"


class CollectionRequest(Base):
    __tablename__ = "collection_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    waste_report_id = Column(
        Integer,
        ForeignKey("waste_reports.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    waste_type = Column(String(50), nullable=False)
    quantity = Column(String(100), nullable=True)
    location = Column(Text, nullable=False)
    additional_notes = Column(Text, nullable=True)
    status = Column(
        String(30),
        default=CollectionStatus.SUBMITTED.value,
        nullable=False,
    )
    requested_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="collection_requests")
    waste_report = relationship("WasteReport", back_populates="collection_request")

    def __repr__(self) -> str:
        return (
            f"<CollectionRequest(id={self.id}, user_id={self.user_id}, "
            f"status='{self.status}')>"
        )
