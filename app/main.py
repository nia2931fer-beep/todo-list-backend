from fastapi import FastAPI

app = FastAPI(
    title = "Tod List API",
    description = "Back end distema todo list",
    version = "0.0.1",
)

@app.get("/", tags=["Status"], summary="verificar se a api está no ar")
def raiz() -> dict[str, str]:
    return{"mensagem": "todo-list online", "documentacao": "/docs"}