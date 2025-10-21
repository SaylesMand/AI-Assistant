import httpx

from contextlib import asynccontextmanager
from fastapi import APIRouter, HTTPException, Request

from src.api.schemas import QueryRequest, QueryResponse
from src.agent_router import load_router_agent


@asynccontextmanager
async def lifespan(app: APIRouter):
    """Инициализирует Router Agent при запуске."""

    # Router Agent
    print("[INFO] Инициализация Router Agent...")
    app.state.router_agent = load_router_agent()
    print("[INFO] Router Agent успешно запущен")

    yield


router = APIRouter(prefix="/agent", lifespan=lifespan)


@router.post("/ask", response_model=QueryResponse)
async def ask_agent(request: Request, query: QueryRequest):
    """Ответ от Агента-оркерстратора"""
    router_agent = getattr(request.app.state, "router_agent", None)
    if router_agent is None:
        raise HTTPException(status_code=500, detail="Router Agent не инициализирован")
    try:
        answer = router_agent.ask(query.question)
        return QueryResponse(answer=answer)
    except httpx.HTTPStatusError as e:
        # Ловим ошибки, которые возвращает API Mistral
        code = e.response.status_code
        if code == 429:
            detail = "Сервис перегружен (Mistral 429). Попробуйте позже."
        elif code == 400:
            detail = "Ошибка в запросе к модели (400). Проверьте формат запроса."
        elif code >= 500:
            detail = "Проблема на стороне модели (500). Попробуйте позже."
        else:
            detail = f"Ошибка при обращении к LLM: {e.response.text}"
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=code, detail=detail)

    except Exception as e:
        # Все остальные ошибки
        print(f"[ERROR] {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Неизвестная ошибка при работе с агентом: {str(e)}",
        )
