"""SQLAlchemy model for export preferences."""
from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.utils.database import Base


class ExportPreferences(Base):
    """User export preferences model."""
    
    __tablename__ = "export_preferences"
    
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    default_format: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default='csv'
    )
    include_metadata: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default='false'
    )
    pretty_json: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default='false'
    )
    csv_include_bom: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default='false'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    __table_args__ = (
        CheckConstraint("default_format IN ('csv', 'json')", name='ck_export_preferences_format'),
    )
    
    def __repr__(self) -> str:
        """String representation of ExportPreferences."""
        return f"<ExportPreferences(user_id={self.user_id}, format='{self.default_format}')>"
