from decimal import Decimal

import pytest

from ai_jobs.services.vacancy import (
    compare_vacancies,
    create_vacancy,
    get_similar_vacancies,
)
from tests.unit.test_vacancy_service import make_vacancy_data


def create_test_vacancy(db_session, reference_ids, **overrides):
    """Create and persist a vacancy for business-operation tests."""
    data = make_vacancy_data(reference_ids, **overrides)
    vacancy = create_vacancy(db_session, data)
    db_session.commit()
    db_session.refresh(vacancy)
    return vacancy


def test_get_similar_vacancies_by_shared_skills(db_session, reference_ids):
    first = create_test_vacancy(db_session, reference_ids)
    second = create_test_vacancy(
        db_session,
        reference_ids,
        salary_usd=Decimal("110000.00"),
    )
    third = create_test_vacancy(
        db_session,
        reference_ids,
        skill_ids=[reference_ids["python_skill_id"]],
        salary_usd=Decimal("90000.00"),
    )

    results = get_similar_vacancies(db_session, first.id)

    assert [item["vacancy"].id for item in results] == [second.id, third.id]
    assert [item["shared_skills_count"] for item in results] == [2, 1]


def test_get_similar_vacancies_respects_limit(db_session, reference_ids):
    first = create_test_vacancy(db_session, reference_ids)
    create_test_vacancy(db_session, reference_ids)
    create_test_vacancy(db_session, reference_ids)

    results = get_similar_vacancies(db_session, first.id, limit=1)

    assert len(results) == 1


def test_get_similar_vacancies_returns_none_for_missing_id(
    db_session,
):
    assert get_similar_vacancies(db_session, 999) is None


def test_get_similar_vacancies_excludes_different_specialization(
    db_session,
    reference_ids,
):
    first = create_test_vacancy(db_session, reference_ids)

    results = get_similar_vacancies(db_session, first.id)

    assert all(
        item["vacancy"].specialization_id == first.specialization_id for item in results
    )


def test_compare_vacancies_returns_comparison(db_session, reference_ids):
    first = create_test_vacancy(
        db_session,
        reference_ids,
        salary_usd=Decimal("100000.00"),
    )
    second = create_test_vacancy(
        db_session,
        reference_ids,
        salary_usd=Decimal("120000.00"),
    )

    result = compare_vacancies(db_session, [first.id, second.id])

    assert result is not None
    assert [item.id for item in result["vacancies"]] == [first.id, second.id]
    assert result["average_salary"] == Decimal("110000.00")
    assert result["salary_difference"] == Decimal("20000.00")
    assert result["highest_paid_vacancy_id"] == second.id
    assert result["lowest_paid_vacancy_id"] == first.id


def test_compare_vacancies_preserves_requested_order(db_session, reference_ids):
    first = create_test_vacancy(db_session, reference_ids)
    second = create_test_vacancy(db_session, reference_ids)

    result = compare_vacancies(db_session, [second.id, first.id])

    assert result is not None
    assert [item.id for item in result["vacancies"]] == [second.id, first.id]


def test_compare_vacancies_returns_none_if_id_is_missing(db_session, reference_ids):
    vacancy = create_test_vacancy(db_session, reference_ids)

    result = compare_vacancies(db_session, [vacancy.id, 999])

    assert result is None


def test_compare_vacancies_with_equal_salaries(db_session, reference_ids):
    first = create_test_vacancy(db_session, reference_ids)
    second = create_test_vacancy(db_session, reference_ids)

    result = compare_vacancies(db_session, [first.id, second.id])

    assert result is not None
    assert result["salary_difference"] == Decimal("0.00")
    assert result["highest_paid_vacancy_id"] == first.id
    assert result["lowest_paid_vacancy_id"] == first.id


def test_compare_vacancies_with_empty_ids(db_session):
    with pytest.raises(ValueError, match="Between 2 and 5"):
        compare_vacancies(db_session, [])
