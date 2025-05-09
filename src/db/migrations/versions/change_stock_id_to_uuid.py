"""change stock id to uuid

Revision ID: change_stock_id_to_uuid
Revises: add_stock_columns
Create Date: 2024-03-21 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "change_stock_id_to_uuid"
down_revision: Union[str, None] = "add_stock_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. UUID 확장 활성화
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # 2. 임시 컬럼 추가
    op.add_column("stocks", sa.Column("new_id", postgresql.UUID(), nullable=True))
    op.add_column("price", sa.Column("new_stock_id", postgresql.UUID(), nullable=True))

    # 3. 임시 컬럼에 UUID 값 할당
    op.execute("UPDATE stocks SET new_id = uuid_generate_v4()")
    op.execute(
        """
        UPDATE price p
        SET new_stock_id = s.new_id
        FROM stocks s
        WHERE p.stock_id = s.id
    """
    )

    # 4. 기존 외래 키 제약 조건 삭제
    op.drop_constraint("price_stock_id_fkey", "price", type_="foreignkey")

    # 5. 기존 id 컬럼 삭제
    op.drop_constraint("stocks_pkey", "stocks", type_="primary")
    op.drop_column("stocks", "id")
    op.drop_column("price", "stock_id")

    # 6. 임시 컬럼을 id로 변경
    op.alter_column("stocks", "new_id", new_column_name="id")
    op.alter_column("price", "new_stock_id", new_column_name="stock_id")

    # 7. 기본키 제약조건 추가
    op.create_primary_key("stocks_pkey", "stocks", ["id"])
    op.create_foreign_key(
        "price_stock_id_fkey",
        "price",
        "stocks",
        ["stock_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 8. NOT NULL 제약조건 추가
    op.alter_column("stocks", "id", nullable=False)
    op.alter_column("price", "stock_id", nullable=False)


def downgrade() -> None:
    # 1. 임시 컬럼 추가
    op.add_column("stocks", sa.Column("new_id", sa.Integer(), nullable=True))
    op.add_column("price", sa.Column("new_stock_id", sa.Integer(), nullable=True))

    # 2. 시퀀스 생성
    op.execute("CREATE SEQUENCE stocks_id_seq")

    # 3. 임시 컬럼에 시퀀스 값 할당
    op.execute("UPDATE stocks SET new_id = nextval('stocks_id_seq')")
    op.execute(
        """
        UPDATE price p
        SET new_stock_id = s.new_id
        FROM stocks s
        WHERE p.stock_id = s.id
    """
    )

    # 4. 기존 외래 키 제약 조건 삭제
    op.drop_constraint("price_stock_id_fkey", "price", type_="foreignkey")

    # 5. 기존 id 컬럼 삭제
    op.drop_constraint("stocks_pkey", "stocks", type_="primary")
    op.drop_column("stocks", "id")
    op.drop_column("price", "stock_id")

    # 6. 임시 컬럼을 id로 변경
    op.alter_column("stocks", "new_id", new_column_name="id")
    op.alter_column("price", "new_stock_id", new_column_name="stock_id")

    # 7. 기본키 제약조건 추가
    op.create_primary_key("stocks_pkey", "stocks", ["id"])
    op.create_foreign_key(
        "price_stock_id_fkey",
        "price",
        "stocks",
        ["stock_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 8. NOT NULL 제약조건 추가
    op.alter_column("stocks", "id", nullable=False)
    op.alter_column("price", "stock_id", nullable=False)

    # 9. 시퀀스 삭제
    op.execute("DROP SEQUENCE IF EXISTS stocks_id_seq")
