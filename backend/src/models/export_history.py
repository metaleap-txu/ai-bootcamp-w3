"""SQLAlchemy model for export history."""
from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.utils.database import Base


class ExportHistory(Base):
    """Export operation history model."""
    
    __tablename__ = "export_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    query_history_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('query_history.id', ondelete='SET NULL'),
        nullable=True
    )
    format: Mapped[str] = mapped_column(String(10), nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    exported_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    
    __table_args__ = (
        CheckConstraint("format IN ('csv', 'json')", name='ck_export_history_format'),
        CheckConstraint("status IN ('success', 'failed', 'cancelled')", name='ck_export_history_status'),
        CheckConstraint("row_count >= 0", name='ck_export_history_row_count'),
        CheckConstraint("file_size_bytes >= 0", name='ck_export_history_file_size'),
    )
    
    def __repr__(self) -> str:
        """String representation of ExportHistory."""
        return f"<ExportHistory(id={self.id}, format='{self.format}', status='{self.status}')>"
