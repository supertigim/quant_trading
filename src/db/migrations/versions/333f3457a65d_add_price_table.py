"""Add price table

Revision ID: 333f3457a65d
Revises: 9becef9870c3
Create Date: 2024-03-21 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "333f3457a65d"
down_revision: Union[str, None] = "9becef9870c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 임시 컬럼 추가
    op.add_column("stocks", sa.Column("new_id", sa.Integer(), nullable=True))

    # 2. 시퀀스 생성
    op.execute("CREATE SEQUENCE stocks_id_seq")

    # 3. 임시 컬럼에 시퀀스 값 할당
    op.execute("UPDATE stocks SET new_id = nextval('stocks_id_seq')")

    # 4. 기존 id 컬럼 삭제
    op.drop_constraint("stocks_pkey", "stocks", type_="primary")
    op.drop_column("stocks", "id")

    # 5. 임시 컬럼을 id로 변경
    op.alter_column("stocks", "new_id", new_column_name="id")

    # 6. 기본키 제약조건 추가
    op.create_primary_key("stocks_pkey", "stocks", ["id"])

    # 7. 시퀀스를 id 컬럼의 기본값으로 설정
    op.execute(
        "ALTER TABLE stocks ALTER COLUMN id SET DEFAULT nextval('stocks_id_seq')"
    )
    op.execute("ALTER SEQUENCE stocks_id_seq OWNED BY stocks.id")

    # price 테이블 생성
    op.create_table(
        "price",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stocks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_price_id"), "price", ["id"], unique=False)
    op.create_index(
        op.f("ix_price_stock_date"), "price", ["stock_id", "date"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_price_stock_date"), table_name="price")
    op.drop_index(op.f("ix_price_id"), table_name="price")
    op.drop_table("price")

    # 1. 임시 컬럼 추가
    op.add_column("stocks", sa.Column("new_id", sa.Integer(), nullable=True))

    # 2. 시퀀스 생성
    op.execute("CREATE SEQUENCE stocks_id_seq")

    # 3. 임시 컬럼에 시퀀스 값 할당
    op.execute("UPDATE stocks SET new_id = nextval('stocks_id_seq')")

    # 4. 기존 id 컬럼 삭제
    op.drop_constraint("stocks_pkey", "stocks", type_="primary")
    op.drop_column("stocks", "id")

    # 5. 임시 컬럼을 id로 변경
    op.alter_column("stocks", "new_id", new_column_name="id")

    # 6. 기본키 제약조건 추가
    op.create_primary_key("stocks_pkey", "stocks", ["id"])

    # 7. 시퀀스 삭제
    op.execute("DROP SEQUENCE IF EXISTS stocks_id_seq")
