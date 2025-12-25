"""SQLAlchemy model for query history."""
from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.utils.database import Base


class QueryHistory(Base):
    """Query history model."""
    
    __tablename__ = "query_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    connection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("connections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    def __repr__(self) -> str:
        """String representation of QueryHistory."""
        status = "SUCCESS" if self.success else "FAILED"
        return f"<QueryHistory(id={self.id}, connection_id={self.connection_id}, status={status})>"
