import os
import uuid
from datetime import datetime, timezone
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)


def get_upload_path(user_id: str, filename: str) -> str:
    now = datetime.now(timezone.utc)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    file_uuid = str(uuid.uuid4())
    relative_path = f"{user_id}/{now.year}/{now.month:02d}/{file_uuid}.{ext}"
    full_path = os.path.join(settings.UPLOAD_DIR, relative_path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    return full_path


async def save_upload_file(file_content: bytes, file_path: str) -> str:
    with open(file_path, "wb") as f:
        f.write(file_content)

    logger.info(f"文件保存成功: {file_path}")
    return file_path


def delete_file(file_path: str) -> bool:
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"文件删除成功: {file_path}")
        return True
    return False
