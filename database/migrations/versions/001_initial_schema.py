"""001 Initial Schema for SupplyTwinAI

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-01 19:51:00.000000

"""
from alembic import op
import sqlalchemy as sa
from backend.app.db.base import Base
from backend.app.models import *

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Use SQLAlchemy Base metadata to create all tables dynamically
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
