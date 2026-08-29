"""Create the initial migration baseline."""

from collections.abc import Sequence

revision: str = "0001_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Register the empty baseline before domain models are introduced."""


def downgrade() -> None:
    """Keep the baseline reversible without dropping domain tables."""
