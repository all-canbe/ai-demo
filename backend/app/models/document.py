from sqlalchemy import String, Integer, ForeignKey, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid
import enum


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PARSING = "parsing"
    EXTRACTING = "extracting"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingStatusType(TypeDecorator):
    impl = String(20)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, ProcessingStatus):
            return value.value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return ProcessingStatus(value)


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    folder_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("folders.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        ProcessingStatusType,
        default=ProcessingStatus.PENDING.value,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    user = relationship("User", back_populates="documents")
    folder = relationship("Folder", back_populates="documents")
