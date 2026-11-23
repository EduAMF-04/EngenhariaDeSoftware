import sqlite3
from pathlib import Path

# O banco será salvo na raiz do projeto como chamados.db (ignorado pelo .gitignore)
DB_PATH = Path(__file__).resolve().parent.parent / "chamados.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Obrigatório no SQLite para ativar chaves estrangeiras e o ON DELETE RESTRICT
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de Usuários (Requirement: Tabela de Usuários)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            perfil TEXT NOT NULL CHECK (perfil IN ('CLIENTE', 'TECNICO')),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Tabela de Chamados (Requirement: Tabela de Chamados & Integridade Referencial)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ABERTO'
                CHECK (status IN ('ABERTO', 'EM_ANDAMENTO', 'RESOLVIDO', 'FECHADO')),
            prioridade TEXT NOT NULL
                CHECK (prioridade IN ('BAIXA', 'MEDIA', 'ALTA')),
            cliente_id INTEGER NOT NULL,
            tecnico_id INTEGER NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES usuarios(id) ON DELETE RESTRICT,
            FOREIGN KEY (tecnico_id) REFERENCES usuarios(id) ON DELETE RESTRICT
        );
    """)

    conn.commit()
    conn.close()