from decimal import Decimal

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_vacancies: int
    average_salary: Decimal | None
    median_salary: Decimal | None
    countries_count: int
    specializations_count: int


class SalaryBySpecialization(BaseModel):
    specialization: str
    vacancies_count: int
    average_salary: Decimal
    min_salary: Decimal
    max_salary: Decimal


class TopSkill(BaseModel):
    skill: str
    vacancies_count: int


class DemandByCountry(BaseModel):
    country: str
    vacancies_count: int


class DemandBySpecialization(BaseModel):
    specialization: str
    vacancies_count: int


class DemandAnalytics(BaseModel):
    by_country: list[DemandByCountry]
    by_specialization: list[DemandBySpecialization]
