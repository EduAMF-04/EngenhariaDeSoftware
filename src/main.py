import sqlite3
from typing import Literal, Optional
from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from src.database import get_connection, init_db

app = FastAPI(
    title="Sistema de Chamados de Suporte",
    description="API RESTful com CRUD completo implementada a partir das especificações OpenSpec.",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    init_db()


# ==========================================
# Schemas de Validação (Pydantic)
# ==========================================

class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2)
    email: str = Field(..., min_length=5)
    perfil: str  # Validado manualmente para retornar 400 conforme a spec


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2)
    email: Optional[str] = Field(None, min_length=5)
    perfil: Optional[str] = None


class ChamadoCreate(BaseModel):
    titulo: str = Field(..., min_length=3)
    descricao: str = Field(..., min_length=5)
    prioridade: Literal["BAIXA", "MEDIA", "ALTA"]
    cliente_id: int


class ChamadoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3)
    descricao: Optional[str] = Field(None, min_length=5)
    prioridade: Optional[Literal["BAIXA", "MEDIA", "ALTA"]] = None
    status: Optional[Literal["ABERTO", "EM_ANDAMENTO", "RESOLVIDO", "FECHADO"]] = None
    tecnico_id: Optional[int] = None


# ==========================================
# CRUD de Usuários
# ==========================================

@app.post("/usuarios", status_code=status.HTTP_201_CREATED, tags=["Usuários"])
def criar_usuario(usuario: UsuarioCreate):
    # Scenario: Tentativa de criar usuário com perfil inválido -> 400 Bad Request
    if usuario.perfil not in ("CLIENTE", "TECNICO"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil inválido. Valores aceitos: 'CLIENTE' ou 'TECNICO'.",
        )

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, perfil) VALUES (?, ?, ?)",
            (usuario.nome, usuario.email, usuario.perfil),
        )
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (novo_id,))
        return dict(cursor.fetchone())
    except sqlite3.IntegrityError:
        # Scenario: Persistência de usuário com e-mail único
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um usuário cadastrado com este e-mail.",
        )
    finally:
        conn.close()


@app.get("/usuarios", tags=["Usuários"])
def listar_usuarios():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM usuarios ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/usuarios/{usuario_id}", tags=["Usuários"])
def buscar_usuario(usuario_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return dict(row)


@app.put("/usuarios/{usuario_id}", tags=["Usuários"])
def atualizar_usuario(usuario_id: int, dados: UsuarioUpdate):
    if dados.perfil is not None and dados.perfil not in ("CLIENTE", "TECNICO"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil inválido. Valores aceitos: 'CLIENTE' ou 'TECNICO'.",
        )

    conn = get_connection()
    cursor = conn.cursor()
    atual = cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    if not atual:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    novo_nome = dados.nome if dados.nome is not None else atual["nome"]
    novo_email = dados.email if dados.email is not None else atual["email"]
    novo_perfil = dados.perfil if dados.perfil is not None else atual["perfil"]

    try:
        cursor.execute(
            "UPDATE usuarios SET nome = ?, email = ?, perfil = ? WHERE id = ?",
            (novo_nome, novo_email, novo_perfil, usuario_id),
        )
        conn.commit()
        atualizado = cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        return dict(atualizado)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está em uso por outro usuário.",
        )
    finally:
        conn.close()


@app.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Usuários"])
def excluir_usuario(usuario_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    atual = cursor.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    if not atual:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    try:
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        # Scenario: Exclusão de usuário com chamados ativos ou históricos -> 409 Conflict
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir o usuário pois existem chamados vinculados a ele.",
        )
    finally:
        conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==========================================
# CRUD de Chamados
# ==========================================

def _buscar_chamado_detalhado(conn: sqlite3.Connection, chamado_id: int):
    query = """
        SELECT
            c.id,
            c.titulo,
            c.descricao,
            c.status,
            c.prioridade,
            c.cliente_id,
            cli.nome AS cliente_nome,
            c.tecnico_id,
            tec.nome AS tecnico_nome,
            c.criado_em
        FROM chamados c
        INNER JOIN usuarios cli ON c.cliente_id = cli.id
        LEFT JOIN usuarios tec ON c.tecnico_id = tec.id
        WHERE c.id = ?
    """
    row = conn.execute(query, (chamado_id,)).fetchone()
    return dict(row) if row else None


@app.post("/chamados", status_code=status.HTTP_201_CREATED, tags=["Chamados"])
def criar_chamado(chamado: ChamadoCreate):
    conn = get_connection()
    cursor = conn.cursor()

    # Verifica existência do cliente (Scenario: Abertura de chamado com cliente inexistente -> 404)
    cliente = cursor.execute("SELECT id, perfil FROM usuarios WHERE id = ?", (chamado.cliente_id,)).fetchone()
    if not cliente:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")

    if cliente["perfil"] != "CLIENTE":
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O usuário informado como solicitante precisa ter o perfil 'CLIENTE'.",
        )

    # Scenario: Abertura de chamado válida -> status='ABERTO', tecnico_id=None
    cursor.execute(
        """
        INSERT INTO chamados (titulo, descricao, status, prioridade, cliente_id, tecnico_id)
        VALUES (?, ?, 'ABERTO', ?, ?, NULL)
        """,
        (chamado.titulo, chamado.descricao, chamado.prioridade, chamado.cliente_id),
    )
    conn.commit()
    novo_id = cursor.lastrowid
    criado = _buscar_chamado_detalhado(conn, novo_id)
    conn.close()
    return criado


@app.get("/chamados", tags=["Chamados"])
def listar_chamados(
    status_filtro: Optional[Literal["ABERTO", "EM_ANDAMENTO", "RESOLVIDO", "FECHADO"]] = Query(
        None, alias="status"
    )
):
    conn = get_connection()
    query = """
        SELECT
            c.id,
            c.titulo,
            c.descricao,
            c.status,
            c.prioridade,
            c.cliente_id,
            cli.nome AS cliente_nome,
            c.tecnico_id,
            tec.nome AS tecnico_nome,
            c.criado_em
        FROM chamados c
        INNER JOIN usuarios cli ON c.cliente_id = cli.id
        LEFT JOIN usuarios tec ON c.tecnico_id = tec.id
    """
    if status_filtro:
        # Scenario: Listagem de chamados com filtro por status
        query += " WHERE c.status = ? ORDER BY c.id"
        rows = conn.execute(query, (status_filtro,)).fetchall()
    else:
        query += " ORDER BY c.id"
        rows = conn.execute(query).fetchall()

    conn.close()
    return [dict(row) for row in rows]


@app.get("/chamados/{chamado_id}", tags=["Chamados"])
def buscar_chamado(chamado_id: int):
    conn = get_connection()
    chamado = _buscar_chamado_detalhado(conn, chamado_id)
    conn.close()
    if not chamado:
        # Scenario: Busca de chamado inexistente -> 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado.")
    return chamado


@app.patch("/chamados/{chamado_id}", tags=["Chamados"])
def atualizar_chamado(chamado_id: int, dados: ChamadoUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    atual = cursor.execute("SELECT * FROM chamados WHERE id = ?", (chamado_id,)).fetchone()
    if not atual:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado.")

    novo_tecnico_id = dados.tecnico_id if dados.tecnico_id is not None else atual["tecnico_id"]
    novo_status = dados.status if dados.status is not None else atual["status"]

    # Scenario: Atribuição de técnico válido
    if dados.tecnico_id is not None:
        tecnico = cursor.execute("SELECT id, perfil FROM usuarios WHERE id = ?", (dados.tecnico_id,)).fetchone()
        if not tecnico:
            conn.close()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Técnico não encontrado.")
        if tecnico["perfil"] != "TECNICO":
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O usuário informado para atribuição deve possuir perfil 'TECNICO'.",
            )

    # Scenario: Bloqueio de fechamento sem técnico atribuído -> 422 Unprocessable Entity
    if novo_status == "FECHADO" and novo_tecnico_id is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Não é possível fechar um chamado sem um técnico atribuído.",
        )

    novo_titulo = dados.titulo if dados.titulo is not None else atual["titulo"]
    nova_descricao = dados.descricao if dados.descricao is not None else atual["descricao"]
    nova_prioridade = dados.prioridade if dados.prioridade is not None else atual["prioridade"]

    cursor.execute(
        """
        UPDATE chamados
        SET titulo = ?, descricao = ?, status = ?, prioridade = ?, tecnico_id = ?
        WHERE id = ?
        """,
        (novo_titulo, nova_descricao, novo_status, nova_prioridade, novo_tecnico_id, chamado_id),
    )
    conn.commit()
    atualizado = _buscar_chamado_detalhado(conn, chamado_id)
    conn.close()
    return atualizado


@app.delete("/chamados/{chamado_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Chamados"])
def excluir_chamado(chamado_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    atual = cursor.execute("SELECT id FROM chamados WHERE id = ?", (chamado_id,)).fetchone()
    if not atual:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado.")

    # Scenario: Remoção de chamado com sucesso -> 204 No Content
    cursor.execute("DELETE FROM chamados WHERE id = ?", (chamado_id,))
    conn.commit()
    conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)