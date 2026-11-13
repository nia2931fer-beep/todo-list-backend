"""Ponto de entrada: cria o app e registra as rotas."""
 
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse 
from app.api.routers import tasks, usuario
from app.core.config import obter_configuracao
from app.core.exceptions import (
    AcessoNaoEncontrado,
    EmailJaCadastrado,
    ErroDeDominio,
    NaoAutenticado,
    RecursoNaoEncontrado,
    RegraDeNegocioViolada,

)
from app.db.database import criar_tabelas
 
STATUS_POR_ERRO: tuple[tuple[type[ErroDeDominio], int], ...] = (
    (RecursoNaoEncontrado, 404),
    (EmailJaCadastrado, 409),
    (NaoAutenticado, 401),
    (AcessoNaoEncontrado, 403),
    (RegraDeNegocioViolada, 422),
    (ErroDeDominio, 400),
    
)
 
@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI) -> AsyncIterator[None]:
    """Prepara o banco na subida da aplicação: cria as tabelas que faltam."""
    obter_configuracao().segredo_jwt()
    criar_tabelas()  # roda quando a API sobe
    yield            # (o que viesse depois do yield rodaria ao desligar)
 
app = FastAPI(
    title="Todo List API",
    description="Backend do ToDo List — curso Desenvolvedor Full Stack (SENAC).",
    version="0.10.0",
    lifespan=ciclo_de_vida,  # liga o ciclo de vida à aplicação
)
 
@app.exception_handler(ErroDeDominio)
async def tratar_erro_dominio(
      _request: Request, excecao: ErroDeDominio
) -> JSONResponse:
    """Converte qualquer erro de domínio na resposta HTTP corresponde.
    
    Um único tratador atende a hierarquia inteira de exceção - é polimorfismo
    aplicação ao tratamento de erro. As rotinas não precisam conhecer códigos de 
    status de negócio e o domínio não precisa conhecer HTTP.
    """
    codigo = next(
        (codigo for tipo, codigo in STATUS_POR_ERRO if isinstance(excecao, tipo)), 400
    )
    cabecalhos = {"WWW-Authenticate": "Bearer"} if codigo == 401 else None
    return JSONResponse(
        status_code=codigo, content={"detail": excecao.mensagem}, headers=cabecalhos
        )
def _mensagem_de_validacao(erro: dict[str, Any]) -> tuple[str, str]:
    """Traduzir um erro do Pydantic em (campo, mensagem em português)."""
    campo = str(erro["loc"][-1]) if erro.get("loc") else "dados"
    tipo = erro.get("type", "")
    ctx = erro.get("ctx", {})
    mensagem = {
        "missing": f"O campo '{campo}' é obrigatório.",
        "string_too_short": f"O campo '{campo}' precisa ter pelo menos "
        f"{ctx.get('min_length')}caractere(s).",
        "string_too_long": f"O campo '{campo}' pode ter no máximo "
        f"{ctx.get('max_length')}caracteres.",
        "enum": f"Valor inválido em '{campo}'. valores aceitos: "
        f"{str(ctx.get('expected', '')).replace(' or ', ' ou ')}.",
        "date_parsing": f"Data inválida em '{campo}'. Use o formato AAAA-MM-DD.",
        "data_from_datetime_parsing":f"Data inválida em '{campo}'. Use o formato AAAA-MM-DD.",
        "int_parsing": f"O campo '{campo} precisa ser no múmero inteiro.",
        "greater_than_equal": f"O campo '{campo}' precisa ser no mínimo {ctx.get('le')}.",
        "less_than_equal": f"O campo '{campo}' pode ser no máximo {ctx.get('le')}.",
        "json_invalid": "O corpo da requisição não é um JSON válido.",
    }
    if tipo == "value_error":
        if campo == "email":
            return campo, "E-mail inválido."
        # Mensagem dos nossos próprios validadores já estão em português.
        return campo, str(erro.get("msg", "")).removeprefix("Value error, ")
    return campo, mensagem.get(tipo, f"Valor Inválido em '{campo}'.")
@app.exception_handler(RequestValidationError)
async def tratar_erro_de_validacao(
    request: Request, excecao: RequestValidationError
) -> JSONResponse:
    """Traduz erros de validação do ptdantic em respostas HTTP 422. """
    erros = [
        {"campo": campo, "mensagem": mensagem}
        for campo, mensagem in map(_mensagem_de_validacao, excecao.errors())
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": erros[0]["mensagem"] if erros else "Dados inválidos.", "erros": erros},
    )

# Registra na aplicação as rotas do arquivo usuarios.py.
app.include_router(usuario.router)
app.include_router(tasks.router)
 
@app.get("/", tags=["Status"], summary="Verificar se a API está no ar")
def raiz() -> dict[str, str]:
    """Confirma que a API está no ar e indica onde está a documentação."""
    return {"mensagem": "Todo List API no ar", "documentacao": "/docs"}
 