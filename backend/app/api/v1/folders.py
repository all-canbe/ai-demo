from fastapi import APIRouter, Query
from typing import Optional
from app.api.deps import DBSession, CurrentUser
from app.schemas.common import ApiResponse
from app.schemas.folder import FolderCreateRequest, FolderItem
from app.services import folder_service

router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("")
async def create_folder(
    db: DBSession,
    current_user: CurrentUser,
    data: FolderCreateRequest,
):
    folder = await folder_service.create_folder(
        db=db,
        user=current_user,
        name=data.name,
        parent_id=data.parent_id,
    )
    return ApiResponse(
        data=FolderItem(
            id=folder.id,
            name=folder.name,
            parent_id=folder.parent_id,
            create_time=folder.created_at,
        )
    )


@router.get("")
async def get_folders(
    db: DBSession,
    current_user: CurrentUser,
    parent_id: Optional[str] = Query(None),
):
    folders = await folder_service.get_folder_list(
        db=db,
        user=current_user,
        parent_id=parent_id,
    )
    items = [
        FolderItem(
            id=f.id,
            name=f.name,
            parent_id=f.parent_id,
            create_time=f.created_at,
        )
        for f in folders
    ]
    return ApiResponse(data=items)


@router.get("/{folder_id}")
async def get_folder_detail(
    db: DBSession,
    current_user: CurrentUser,
    folder_id: str,
):
    folder = await folder_service.get_folder_detail(db, folder_id, current_user)
    return ApiResponse(
        data=FolderItem(
            id=folder.id,
            name=folder.name,
            parent_id=folder.parent_id,
            create_time=folder.created_at,
        )
    )


@router.put("/{folder_id}")
async def update_folder(
    db: DBSession,
    current_user: CurrentUser,
    folder_id: str,
    data: FolderCreateRequest,
):
    folder = await folder_service.update_folder(
        db=db,
        folder_id=folder_id,
        user=current_user,
        name=data.name,
        parent_id=data.parent_id,
    )
    return ApiResponse(
        data=FolderItem(
            id=folder.id,
            name=folder.name,
            parent_id=folder.parent_id,
            create_time=folder.created_at,
        )
    )


@router.delete("/{folder_id}")
async def delete_folder(
    db: DBSession,
    current_user: CurrentUser,
    folder_id: str,
):
    await folder_service.delete_folder(db, folder_id, current_user)
    return ApiResponse(message="文件夹删除成功")
