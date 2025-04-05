"""add_product_hs

Revision ID: b2cf6e1c1f29
Revises: 4db8388dcc33
Create Date: 2025-04-02 18:13:30.390209

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2cf6e1c1f29"
down_revision: Union[str, None] = "4db8388dcc33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "producthss",
        sa.Column("code_mark_head", sa.String(), nullable=False),
        sa.Column("code_hs", sa.String(), nullable=False),
        sa.Column("code_customs", sa.String(), nullable=False),
        sa.Column("inn_supplier", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("brand", sa.String(), nullable=False),
        sa.Column("name_supplier", sa.String(), nullable=False),
        sa.Column("data_in", sa.Date(), nullable=False),
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code_mark_head"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("producthss")
    # ### end Alembic commands ###
