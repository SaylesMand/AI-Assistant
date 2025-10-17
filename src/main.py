from fastapi import FastAPI
from src.api.routers import router


app = FastAPI()
app.include_router(router)

# question = "Из чего состоит архитектура MaxPatrol 10?"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
