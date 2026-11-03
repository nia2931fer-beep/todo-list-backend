"""Entidade Usuario: representa um usuário do sistema, com nome, e-mail e senha (em hash)."""
from __future__ import annotations
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import validates
from app.core.datas import agora_utc
from app.core.exceptions import ValorInvalido
from app.core.security import HashDeSenha
from app.db.database import Base
 
class Usuario(Base):
    """Usuário do sistema."""
 
    # Nome da tabela no banco de dados.
    __tablename__ = "usuarios"
 
    # Cada Column(...) vira uma coluna da tabela.
    id = Column(Integer, primary_key=True, index=True)          # chave primária
    nome = Column(String(120), nullable=False)                   # obrigatório
    email = Column(String(180), nullable=False, unique=True, index=True)  # não repete
 
    # O hash é privado: nenhuma camada acima precisa — nem deve — ler este
    # valor. Quem quiser conferir uma senha usa `senha_confere`.
    # No banco a coluna se chama "senha_hash"; no Python, "_senha_hash".
    _senha_hash = Column("senha_hash", String(255), nullable=False)
 
    # default=agora_utc: preenchido sozinho com a data/hora atual ao gravar.
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
 
    def __init__(self, *, nome: str, email: str) -> None:
        """Cria um usuário ainda sem senha definida. """
        # O "*" obriga a passar nome= e email= pelo nome. Não há parâmetro de senha.
        self.nome = nome
        self.email = self.normalizar_email(email)
 
    @staticmethod
    def normalizar_email(email: str) -> str:
        """Normaliza o e-mail para facilitar comparações e buscas."""
        # strip() tira espaços das pontas; lower() deixa tudo minúsculo.
        return email.strip().lower()
 
    def definir_senha(self, senha: str, hasher: HashDeSenha) -> None:
        """Define a senha do usuário, gravando apenas o hash. """
        # Único caminho para gravar a senha: ela nunca fica em texto puro.
        self._senha_hash = hasher.gerar(senha)
 
    def senha_confere(self, senha: str, hasher: HashDeSenha) -> bool:
        """Informa se a senha apresentada corresponde à cadastrada."""
        return hasher.verificar(senha, self._senha_hash)
 
    @validates("nome")
    def _validar_nome(self, _campo: str, valor: str) -> str:
        # Roda toda vez que o nome recebe um valor.
        if not valor or not valor.strip():
            raise ValorInvalido("O nome do usuário não pode ficar vazio.")
        return valor.strip()
 
    def __repr__(self) -> str:
        # Como o objeto aparece ao ser impresso (ajuda na depuração).
        return f"<Usuario id={self.id} email={self.email!r}>"