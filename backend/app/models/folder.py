from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid


class Folder(Base, TimestampMixin):
    __tablename__ = "folders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("folders.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    user = relationship("User", back_populates="folders")
    documents = relationship("Document", back_populates="folder", lazy="selectin")
    children = relationship("Folder", backref="parent_folder", remote_side=[id], lazy="selectin")
