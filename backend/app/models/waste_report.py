import enum
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class WasteType(str, enum.Enum):
    ORGANIC = "Organic"
    PLASTIC = "Plastic"
    PAPER = "Paper"
    GLASS = "Glass"
    METAL = "Metal"
    E_WASTE = "E-Waste"
    HAZARDOUS = "Hazardous"
    OTHER = "Other"


class WasteReport(Base):
    __tablename__ = "waste_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_path = Column(String(500), nullable=True)
    waste_type = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    disposal_guidance = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="waste_reports")
    collection_request = relationship(
        "CollectionRequest",
        back_populates="waste_report",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<WasteReport(id={self.id}, user_id={self.user_id}, waste_type='{self.waste_type}')>"
