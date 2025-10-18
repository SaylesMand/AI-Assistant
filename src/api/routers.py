from contextlib import asynccontextmanager
from fastapi import APIRouter, HTTPException, Request

from src.api.schemas import QueryRequest, QueryResponse
from src.rag import build_rag_pipeline
from src.sql_agent import load_sql_agent


@asynccontextmanager
async def lifespan(app: APIRouter):
    """Инициализирует RAG и SQL Agent при запуске."""
    # RAG
    print("[INFO] Инициализация RAG...")
    app.state.rag = build_rag_pipeline()
    print("[INFO] RAG успешно загружен")

    # SQL Agent
    print("[INFO] Инициализация SQL Agent...")
    app.state.sql_agent = load_sql_agent()
    print("[INFO] SQL Agent успешно загружен")

    yield


router = APIRouter(lifespan=lifespan)


@router.post("/rag/ask", response_model=QueryResponse)
async def ask_rag(request: Request, query: QueryRequest):
    """Ответ от RAG-системы."""
    rag = getattr(request.app.state, "rag", None)
    if rag is None:
        raise HTTPException(status_code=500, detail="RAG не инициализирован")

    try:
        answer = rag.ask(query.question)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sql_agent/ask", response_model=QueryResponse)
async def ask_sql_agent(request: Request, query: QueryRequest):
    """Ответ от SQL агента."""
    sql_agent = getattr(request.app.state, "sql_agent", None)
    if sql_agent is None:
        raise HTTPException(status_code=500, detail="SQL Agent не инициализирован")

    try:
        answer = sql_agent.ask(query.question)
        return QueryResponse(answer=str(answer))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
