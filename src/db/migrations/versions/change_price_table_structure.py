"""change price table structure

Revision ID: bd1f6664ae95
Revises: 333f3457a65d
Create Date: 2024-03-21 11:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bd1f6664ae95"
down_revision: Union[str, None] = "333f3457a65d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 임시 컬럼 추가
    op.add_column("price", sa.Column("stock_id", sa.Integer(), nullable=True))

    # 2. stocks 테이블의 id 값을 price 테이블의 stock_id에 복사
    op.execute(
        """
        UPDATE price p
        SET stock_id = s.id
        FROM stocks s
        WHERE p.ticker = s.ticker
    """
    )

    # 3. stock_id를 NOT NULL로 변경
    op.alter_column("price", "stock_id", nullable=False)

    # 4. 기존 외래 키 제약 조건 삭제
    op.drop_constraint("price_ticker_fkey", "price", type_="foreignkey")

    # 5. 새로운 외래 키 제약 조건 추가
    op.create_foreign_key(
        "price_stock_id_fkey",
        "price",
        "stocks",
        ["stock_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 6. 기존 인덱스 삭제
    op.drop_index("ix_price_ticker_date", table_name="price")

    # 7. 새로운 인덱스 생성
    op.create_index("ix_price_stock_date", "price", ["stock_id", "date"], unique=True)

    # 8. ticker 컬럼 삭제
    op.drop_column("price", "ticker")


def downgrade() -> None:
    # 1. ticker 컬럼 추가
    op.add_column("price", sa.Column("ticker", sa.String(length=20), nullable=True))

    # 2. stocks 테이블의 ticker 값을 price 테이블의 ticker에 복사
    op.execute(
        """
        UPDATE price p
        SET ticker = s.ticker
        FROM stocks s
        WHERE p.stock_id = s.id
    """
    )

    # 3. ticker를 NOT NULL로 변경
    op.alter_column("price", "ticker", nullable=False)

    # 4. 기존 외래 키 제약 조건 삭제
    op.drop_constraint("price_stock_id_fkey", "price", type_="foreignkey")

    # 5. 새로운 외래 키 제약 조건 추가
    op.create_foreign_key(
        "price_ticker_fkey",
        "price",
        "stocks",
        ["ticker"],
        ["ticker"],
        ondelete="CASCADE",
    )

    # 6. 기존 인덱스 삭제
    op.drop_index("ix_price_stock_date", table_name="price")

    # 7. 새로운 인덱스 생성
    op.create_index("ix_price_ticker_date", "price", ["ticker", "date"], unique=True)

    # 8. stock_id 컬럼 삭제
    op.drop_column("price", "stock_id")
