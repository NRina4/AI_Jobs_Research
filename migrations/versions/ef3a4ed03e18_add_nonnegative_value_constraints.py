"""add nonnegative value constraints

Revision ID: ef3a4ed03e18
Revises: bc65d7cb8650
Create Date: 2026-11-11 01:12:35.275304

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "ef3a4ed03e18"
down_revision = "bc65d7cb8650"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        op.f("ck_vacancies_salary_min_nonnegative"),
        "vacancies",
        "salary_min >= 0",
    )
    op.create_check_constraint(
        op.f("ck_vacancies_benefits_value_nonnegative"),
        "vacancies",
        "benefits_value_usd >= 0",
    )
    op.create_check_constraint(
        op.f("ck_vacancies_ai_investment_nonnegative"),
        "vacancies",
        "ai_investment_company_millions >= 0",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_vacancies_ai_investment_nonnegative",
        "vacancies",
        type_="check",
    )
    op.drop_constraint(
        "ck_vacancies_benefits_value_nonnegative",
        "vacancies",
        type_="check",
    )
    op.drop_constraint(
        "ck_vacancies_salary_min_nonnegative",
        "vacancies",
        type_="check",
    )
