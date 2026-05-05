from lib.postgresql import create_table, insert_row, select_rows


DB_CONFIG = {
    "host": "localhost",
    "port": 5435,
    "dbname": "appdb",
    "user": "appuser",
    "password": "water",
}


def main():
    create_table(
        "students",
        """
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        age INTEGER CHECK (age >= 0),
        email VARCHAR(255) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """,
        db_config=DB_CONFIG,
    )

    inserted_row = insert_row(
        "students",
        {
            "name": "홍길동",
            "age": 20,
            "email": "hong@example.com",
        },
        returning=["id", "name", "email"],
        db_config=DB_CONFIG,
    )

    print("추가된 데이터:")
    print(inserted_row)

    rows = select_rows(
        "students",
        columns=["id", "name", "age", "email", "created_at"],
        order_by="id",
        order_desc=True,
        limit=10,
        db_config=DB_CONFIG,
    )

    print("조회 결과:")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()