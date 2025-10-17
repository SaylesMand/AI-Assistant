from contextlib import asynccontextmanager
from fastapi import APIRouter, HTTPException, Request

from src.api.schemas import QueryRequest, QueryResponse
from src.rag import build_rag_pipeline


@asynccontextmanager
async def lifespan(app: APIRouter):
    """Загружает RAG при запуске."""
    print("[INFO] Инициализация RAG...")
    app.state.rag = build_rag_pipeline()
    print("[INFO] RAG успешно загружен")

    yield


router = APIRouter(prefix="/rag", lifespan=lifespan)


@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: Request, query: QueryRequest):
    """Обработка запроса без использования global переменной."""
    rag = getattr(request.app.state, "rag", None)
    if rag is None:
        raise HTTPException(status_code=500, detail="RAG не инициализирован")

    try:
        answer = rag.ask(query.question)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
