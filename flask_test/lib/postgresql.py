# lib/postgresql.py

from __future__ import annotations

import os
from typing import Any, Mapping, Sequence

import psycopg
from psycopg import sql
from psycopg.rows import dict_row


def get_db_config(overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """
    PostgreSQL 접속 설정을 생성합니다.

    기본값은 환경변수에서 읽습니다.
    필요하면 overrides로 직접 설정을 덮어쓸 수 있습니다.
    """
    config = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.getenv("PGDATABASE", "appdb"),
        "user": os.getenv("PGUSER", "appuser"),
        "password": os.getenv("PGPASSWORD"),
    }

    if overrides:
        config.update(overrides)

    return config


def get_connection(db_config: Mapping[str, Any] | None = None):
    """
    PostgreSQL 연결 객체를 반환합니다.
    row_factory=dict_row를 사용하여 SELECT 결과를 dict 형태로 받습니다.
    """
    config = get_db_config(db_config)

    if not config.get("password"):
        raise ValueError("PostgreSQL 비밀번호가 설정되지 않았습니다.")

    return psycopg.connect(**config, row_factory=dict_row)


def create_table(
    table_name: str,
    columns_sql: str,
    *,
    schema: str = "public",
    db_config: Mapping[str, Any] | None = None,
) -> None:
    """
    테이블을 생성합니다.

    주의:
    columns_sql은 개발자가 작성한 신뢰 가능한 SQL만 넣어야 합니다.
    사용자 입력값을 columns_sql에 직접 넣으면 안 됩니다.

    예:
    create_table(
        "students",
        '''
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        age INTEGER,
        email VARCHAR(255) UNIQUE
        '''
    )
    """
    if not table_name.strip():
        raise ValueError("table_name이 비어 있습니다.")

    if not columns_sql.strip():
        raise ValueError("columns_sql이 비어 있습니다.")

    query = sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} ({})").format(
        sql.Identifier(schema),
        sql.Identifier(table_name),
        sql.SQL(columns_sql),
    )

    with get_connection(db_config) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
        conn.commit()


def insert_row(
    table_name: str,
    data: Mapping[str, Any],
    *,
    schema: str = "public",
    returning: str | Sequence[str] | None = None,
    db_config: Mapping[str, Any] | None = None,
) -> dict[str, Any] | int:
    """
    테이블에 데이터 1건을 추가합니다.

    예:
    insert_row(
        "students",
        {
            "name": "홍길동",
            "age": 20,
            "email": "hong@example.com"
        },
        returning=["id", "name"]
    )
    """
    if not table_name.strip():
        raise ValueError("table_name이 비어 있습니다.")

    if not data:
        raise ValueError("insert할 data가 비어 있습니다.")

    columns = list(data.keys())
    values = list(data.values())

    column_identifiers = sql.SQL(", ").join(
        sql.Identifier(column) for column in columns
    )

    placeholders = sql.SQL(", ").join(
        sql.Placeholder() for _ in columns
    )

    query = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
        sql.Identifier(schema),
        sql.Identifier(table_name),
        column_identifiers,
        placeholders,
    )

    if returning:
        if isinstance(returning, str):
            returning_columns = [returning]
        else:
            returning_columns = list(returning)

        returning_identifiers = sql.SQL(", ").join(
            sql.Identifier(column) for column in returning_columns
        )

        query += sql.SQL(" RETURNING {}").format(returning_identifiers)

    with get_connection(db_config) as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)

            if returning:
                result = cur.fetchone()
            else:
                result = cur.rowcount

        conn.commit()

    return result


def select_rows(
    table_name: str,
    *,
    columns: Sequence[str] | None = None,
    filters: Mapping[str, Any] | None = None,
    schema: str = "public",
    order_by: str | Sequence[str] | None = None,
    order_desc: bool = False,
    limit: int | None = None,
    db_config: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    테이블 데이터를 조회합니다.

    예:
    select_rows(
        "students",
        columns=["id", "name", "age"],
        filters={"age": 20},
        order_by="id",
        limit=10
    )
    """
    if not table_name.strip():
        raise ValueError("table_name이 비어 있습니다.")

    params: list[Any] = []

    if columns:
        selected_columns = sql.SQL(", ").join(
            sql.Identifier(column) for column in columns
        )
    else:
        selected_columns = sql.SQL("*")

    query = sql.SQL("SELECT {} FROM {}.{}").format(
        selected_columns,
        sql.Identifier(schema),
        sql.Identifier(table_name),
    )

    if filters:
        where_clauses = []

        for column, value in filters.items():
            where_clauses.append(
                sql.SQL("{} = {}").format(
                    sql.Identifier(column),
                    sql.Placeholder(),
                )
            )
            params.append(value)

        query += sql.SQL(" WHERE ") + sql.SQL(" AND ").join(where_clauses)

    if order_by:
        if isinstance(order_by, str):
            order_columns = [order_by]
        else:
            order_columns = list(order_by)

        order_identifiers = sql.SQL(", ").join(
            sql.Identifier(column) for column in order_columns
        )

        direction = sql.SQL("DESC") if order_desc else sql.SQL("ASC")

        query += sql.SQL(" ORDER BY {} {}").format(
            order_identifiers,
            direction,
        )

    if limit is not None:
        if limit <= 0:
            raise ValueError("limit은 1 이상의 정수여야 합니다.")

        query += sql.SQL(" LIMIT {}").format(sql.Placeholder())
        params.append(limit)

    with get_connection(db_config) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

    return list(rows)