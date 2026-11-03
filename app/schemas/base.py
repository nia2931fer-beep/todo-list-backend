"""Peças comuns a todos os schemas: tradução camelCase e datas em UTC."""
from datetime import datetime, timezone
from typing import Annotated
 
from pydantic import AfterValidator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
 
 
def _garantir_utc(valor: datetime) -> datetime:
    """Adiciona o fuso UTC a uma data/hora que não tem fuso. Se já tiver, não altera."""
    # O SQLite não guarda fuso: ao ler do banco a data vem "sem fuso".
    return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)
 
 
# Tipo reutilizável: uma data/hora que sempre sai na resposta com o fuso.
DataHoraUTC = Annotated[datetime, AfterValidator(_garantir_utc)]
 
 
class EsquemaDeEntrada(BaseModel):
    """Base dos schemas que recebem dados do cliente."""
 
    # alias_generator: gera os nomes em camelCase (criado_em -> criadoEm)
    # populate_by_name: aceita também o nome em Python
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
 
 
class EsquemaDeSaida(BaseModel):
    """Base dos schemas que enviam dados para o cliente. As datas sempre saem com fuso UTC.
    """
 
    # from_attributes: permite montar o schema direto a partir de um objeto (ex.: Usuario)
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )