"""Emumerações do domínio.

Antes, os valores válidos de status e prioridades estavam escritos como texto 
solto em três lugares: no `Literal` dos schemas, no `default` das colunas e no 
`case` que ordenava por prioridade. Acrescentar uma priordade nova exigia 
lembrar dos três. aqui eles passam a ter um único lugar de definição.

Herdar de `str` faz cada membro se comportar como o próprio texto - o que
permite gravá-lo em uma coluna `String`, compará-lo com uma string vinda do 
banco e serializá-lo em JSON sem conversão nominal
"""
from enum import Enum

class StatusTarefa(str, Enum):
    """Situação em que uma tarefa pode estar."""

    PENDENTE = "pendente"
    CONCLUIDA = "concluida"

class PrioridadeTarefa(str, Enum):
    """Nível de prioridade se uma tarefa, da menor para a maior."""

    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"
    @property
    def peso(self) -> int:
        """Posição na ordenação por prioridade - 0 é a mais urgente.
        Ordenar pelo texto daria "alta, baixa, media, urgente", que não é a 
        ordem que o usuárioespera ver. O peso existe para isso.
        """
        return _PESOS[self]
    @classmethod
    def mapa_de_pesos(cls)  -> dict[str, int]:
        """Mapa `valor -> peso`, no formato que o `case()` so SQL consome."""
        return {prioridade.value: prioridade.peso for prioridade in cls}
_PESOS = {
    PrioridadeTarefa.URGENTE: 0,
    PrioridadeTarefa.ALTA: 1,
    PrioridadeTarefa.MEDIA: 2,
    PrioridadeTarefa.BAIXA: 3,
}
class CampoOrdenacao(str, Enum):
    """Campos polos quais a listagem de tarefas pode ser ordenada.
    
    Os valores repetem o nome público do compo na API (camelCase), porque é 
    isso que o cliente envia em `?ordenarPor=`. Como é um enum, um valor fora 
    da lista pass a ser recusado com 244 - antes, o código caía 
    silenciosamente na ordenaçao por data de criação e o cliente nunca sabia 
    que seu parâmetro havia sido ignorado.
    """

    CRIADO_EM = "criadoEm"
    PRAZO = "prazo"
    PRIORIDADE = "prioridade"

class Ordem(str, Enum):
    """Sentido da ordenação."""

    ASC = "asc"
    DESC = "desc"