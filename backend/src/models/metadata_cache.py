"""SQLAlchemy model for metadata cache."""
from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.utils.database import Base


class MetadataCache(Base):
    """Metadata cache model."""
    
    __tablename__ = "metadata_cache"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    connection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("connections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schema_name: Mapped[str] = mapped_column(String(255), nullable=False)
    table_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'schemas', 'tables', 'columns'
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    cached_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    def __repr__(self) -> str:
        """String representation of MetadataCache."""
        return (
            f"<MetadataCache(id={self.id}, connection_id={self.connection_id}, "
            f"type={self.metadata_type}, schema={self.schema_name})>"
        )
