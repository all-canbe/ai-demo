from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FolderCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="文件夹名称")
    parent_id: Optional[str] = Field(None, description="父文件夹ID")


class FolderItem(BaseModel):
    id: str
    name: str
    parent_id: Optional[str] = None
    create_time: datetime

    model_config = {"from_attributes": True}
