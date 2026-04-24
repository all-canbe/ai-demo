from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Optional
from app.config.settings import settings


class DocumentUploadResponse(BaseModel):
    id: str
    name: str
    type: str
    size: int
    upload_time: datetime
    processing_status: str

    model_config = {"from_attributes": True}
    
    @computed_field
    @property
    def file_url(self) -> str:
        return f"{settings.API_V1_PREFIX}/documents/{self.id}/download"


class DocumentItem(BaseModel):
    id: str
    name: str
    type: str
    size: int
    upload_time: datetime
    processing_status: str
    folder_id: Optional[str] = None

    model_config = {"from_attributes": True}
    
    @computed_field
    @property
    def file_url(self) -> str:
        return f"{settings.API_V1_PREFIX}/documents/{self.id}/download"


class DocumentStatusResponse(BaseModel):
    id: str
    processing_status: str
    progress: int = 0
    error_message: Optional[str] = None
    updated_at: datetime


class DocumentSummaryResponse(BaseModel):
    document_id: str
    summary: str
    key_points: list[str]
