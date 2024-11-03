from alembic import op  # type: ignore
import sqlalchemy as sa

revision = "031124_add_texts_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "texts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("domain", sa.String, nullable=False),
        sa.Column("audience", sa.String, nullable=True),
        sa.Column("tone", sa.String, nullable=True),
    )


def downgrade():
    op.drop_table("texts")
