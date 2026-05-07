from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
import logging

from services.document_service import document_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/documents/process")
async def process_document(file: UploadFile = File(...)):
    """上传并处理文档"""
    try:
        content = await file.read()
        result = document_service.process_document(file.filename, content)
        return {"status": "success", **result}
    except Exception as e:
        logger.error(f"文档处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/summarize")
async def summarize_document(file: UploadFile = File(...), mode: str = "default"):
    """生成文档摘要"""
    try:
        content = await file.read()
        parsed = document_service.parser.parse(file.filename, content)
        text = document_service._extract_text_from_parsed(parsed)
        summary = document_service.summarize(text, mode)
        return {"status": "success", "summary": summary, "text_length": len(text)}
    except Exception as e:
        logger.error(f"摘要生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/summarize/stream")
async def summarize_document_stream(file: UploadFile = File(...)):
    """流式生成文档摘要"""
    try:
        content = await file.read()
        parsed = document_service.parser.parse(file.filename, content)
        text = document_service._extract_text_from_parsed(parsed)
        
        async def generate():
            for chunk in document_service.summarize(text, use_streaming=True):
                yield chunk
        
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        logger.error(f"流式摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/qa/query")
async def qa_query(question: str):
    """问答查询（非流式）"""
    try:
        result = document_service.query(question, use_streaming=False)
        return {"status": "success", **result}
    except Exception as e:
        logger.error(f"问答查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/qa/query/stream")
async def qa_query_stream(question: str):
    """问答查询（流式）"""
    try:
        async def generate():
            for chunk in document_service.query(question, use_streaming=True):
                yield chunk
        
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        logger.error(f"流式问答失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/key-points")
async def extract_key_points(file: UploadFile = File(...), max_points: int = 5):
    """提取文档关键点"""
    try:
        content = await file.read()
        parsed = document_service.parser.parse(file.filename, content)
        text = document_service._extract_text_from_parsed(parsed)
        key_points = document_service.extract_key_points(text, max_points)
        return {"status": "success", "key_points": key_points}
    except Exception as e:
        logger.error(f"关键点提取失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """获取系统统计信息"""
    try:
        stats = document_service.get_stats()
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/batch-process")
async def batch_process_documents(files: List[UploadFile] = File(...)):
    """批量处理文档"""
    results = []
    for file in files:
        try:
            content = await file.read()
            result = document_service.process_document(file.filename, content)
            results.append({"filename": file.filename, "success": True, **result})
        except Exception as e:
            results.append({"filename": file.filename, "success": False, "error": str(e)})
    
    return {"status": "success", "results": results}
