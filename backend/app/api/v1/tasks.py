from fastapi import APIRouter, Query
from celery.result import AsyncResult
from app.tasks.celery_app import celery_app
from app.schemas.common import ApiResponse
from app.config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        status = result.status
        data = {
            "task_id": task_id,
            "status": status,
            "completed": result.ready(),
            "failed": result.failed(),
        }
        
        if result.ready():
            if result.successful():
                data["result"] = result.result
            else:
                data["error"] = str(result.info)
        
        return ApiResponse(data=data)
    
    except Exception as e:
        logger.error(f"获取任务状态失败: {task_id}, 错误: {e}")
        return ApiResponse(data={"task_id": task_id, "status": "unknown", "error": str(e)})


@router.post("/{task_id}/revoke")
async def revoke_task(task_id: str):
    """取消任务"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        logger.info(f"任务已取消: {task_id}")
        return ApiResponse(message="任务已取消")
    except Exception as e:
        logger.error(f"取消任务失败: {task_id}, 错误: {e}")
        return ApiResponse(success=False, message=f"取消任务失败: {e}")


@router.get("/")
async def get_task_list(
    status: str = Query(None),
    limit: int = Query(10, ge=1, le=100),
):
    """获取任务列表"""
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active() or {}
        
        tasks = []
        for worker, worker_tasks in active_tasks.items():
            for task in worker_tasks[:limit]:
                if status is None or task.get("status") == status:
                    tasks.append({
                        "task_id": task.get("id"),
                        "name": task.get("name"),
                        "args": task.get("args"),
                        "kwargs": task.get("kwargs"),
                        "worker": worker,
                        "status": task.get("status", "active"),
                        "started_at": task.get("time_start"),
                    })
        
        return ApiResponse(data={"tasks": tasks[:limit]})
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        return ApiResponse(success=False, message=f"获取任务列表失败: {e}")


@router.get("/stats")
async def get_task_stats():
    """获取任务统计信息"""
    try:
        inspect = celery_app.control.inspect()
        
        stats = {
            "active": 0,
            "reserved": 0,
            "scheduled": 0,
            "workers": 0,
        }
        
        active = inspect.active() or {}
        stats["active"] = sum(len(tasks) for tasks in active.values())
        
        reserved = inspect.reserved() or {}
        stats["reserved"] = sum(len(tasks) for tasks in reserved.values())
        
        scheduled = inspect.scheduled() or {}
        stats["scheduled"] = sum(len(tasks) for tasks in scheduled.values())
        
        stats["workers"] = len(active)
        
        return ApiResponse(data=stats)
    except Exception as e:
        logger.error(f"获取任务统计失败: {e}")
        return ApiResponse(success=False, message=f"获取任务统计失败: {e}")