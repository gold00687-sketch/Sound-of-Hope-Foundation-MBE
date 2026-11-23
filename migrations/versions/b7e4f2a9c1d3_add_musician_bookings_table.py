"""add_musician_bookings_table

Revision ID: b7e4f2a9c1d3
Revises: 733bec441480
Create Date: 2026-11-14 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b7e4f2a9c1d3"
down_revision: Union[str, None] = "733bec441480"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "musician_bookings",
        sa.Column("act_id", sa.String(length=100), nullable=False),
        sa.Column("act_name", sa.String(length=255), nullable=False),
        sa.Column("booker_name", sa.String(length=255), nullable=False),
        sa.Column("booker_email", sa.String(length=255), nullable=False),
        sa.Column("booker_phone", sa.String(length=50), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("event_location", sa.String(length=255), nullable=False),
        sa.Column("guest_count", sa.Integer(), nullable=True),
        sa.Column("duration_hours", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("fee_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("fee_currency", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_musician_bookings_act_id"), "musician_bookings", ["act_id"], unique=False
    )
    op.create_index(
        op.f("ix_musician_bookings_booker_email"), "musician_bookings", ["booker_email"], unique=False
    )
    op.create_index(
        op.f("ix_musician_bookings_status"), "musician_bookings", ["status"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_musician_bookings_status"), table_name="musician_bookings")
    op.drop_index(op.f("ix_musician_bookings_booker_email"), table_name="musician_bookings")
    op.drop_index(op.f("ix_musician_bookings_act_id"), table_name="musician_bookings")
    op.drop_table("musician_bookings")
