"""Trip manager tables.

Revision ID: 001_initial
Revises:
Create Date: 2026-09-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "trips",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("slug", sa.String(80), nullable=False, unique=True),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("eyebrow", sa.String(80), nullable=False),
        sa.Column("date_label", sa.String(80), nullable=False),
        sa.Column("callout_title", sa.String(200)),
        sa.Column("callout_body", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "route_stops",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(120), nullable=False),
    )
    op.create_table(
        "hotels",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("city", sa.String(200), nullable=False),
        sa.Column("check_in", sa.String(80), nullable=False),
        sa.Column("check_out", sa.String(80), nullable=False),
        sa.Column("nights", sa.Integer(), nullable=False),
    )
    op.create_table(
        "transport_legs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("origin", sa.String(120), nullable=False),
        sa.Column("destination", sa.String(120), nullable=False),
        sa.Column("duration", sa.String(80), nullable=False),
        sa.Column("mode", sa.String(80), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("detail_extra", sa.Text()),
        sa.Column("flag", sa.Text()),
    )
    op.create_table(
        "itinerary_days",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("date_label", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("subtitle", sa.Text(), nullable=False),
        sa.Column("transit", sa.Text()),
        sa.Column(
            "transport_leg_id",
            sa.Uuid(),
            sa.ForeignKey("transport_legs.id", ondelete="SET NULL"),
        ),
    )
    op.create_table(
        "itinerary_tasks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "day_id",
            sa.Uuid(),
            sa.ForeignKey("itinerary_days.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("checked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "flights",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_id", sa.Uuid(), sa.ForeignKey("itinerary_days.id", ondelete="CASCADE")),
        sa.Column("group_label", sa.String(40)),
        sa.Column("group_position", sa.Integer()),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("origin", sa.String(20), nullable=False),
        sa.Column("destination", sa.String(20), nullable=False),
        sa.Column("date_label", sa.String(40)),
        sa.Column("depart_time", sa.String(20), nullable=False),
        sa.Column("arrive_time", sa.String(20), nullable=False),
    )
    op.create_table(
        "packing_sections",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
    )
    op.create_table(
        "packing_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "section_id",
            sa.Uuid(),
            sa.ForeignKey("packing_sections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("checked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "tips",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
    )
    op.create_table(
        "shopping_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.String(200), nullable=False),
        sa.Column("done", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "expenses",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.String(200), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("expenses")
    op.drop_table("shopping_items")
    op.drop_table("tips")
    op.drop_table("packing_items")
    op.drop_table("packing_sections")
    op.drop_table("flights")
    op.drop_table("itinerary_tasks")
    op.drop_table("itinerary_days")
    op.drop_table("transport_legs")
    op.drop_table("hotels")
    op.drop_table("route_stops")
    op.drop_table("trips")
    op.execute("DROP EXTENSION IF EXISTS vector")
