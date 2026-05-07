from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.routes import router
from services.document_service import document_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="智能文档处理系统",
    description="基于FastAPI + LangChain的智能文档处理系统，支持PDF/Word/图片/OCR解析、向量检索、知识图谱构建和LLM问答",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    document_service.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    try:
        document_service.vector_store.close()
        document_service.graph_builder.close()
    except Exception as e:
        logging.warning(f"关闭服务失败: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "智能文档处理系统 API",
        "version": "1.0.0",
        "endpoints": {
            "文档处理": "/api/v1/documents/process",
            "文档摘要": "/api/v1/documents/summarize",
            "流式摘要": "/api/v1/documents/summarize/stream",
            "问答查询": "/api/v1/qa/query",
            "流式问答": "/api/v1/qa/query/stream",
            "关键点提取": "/api/v1/documents/key-points",
            "系统统计": "/api/v1/stats",
            "批量处理": "/api/v1/documents/batch-process"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
