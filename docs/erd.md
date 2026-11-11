# ER-диаграмма базы данных

База данных включает 11 связанных таблиц: справочники, основную таблицу `vacancies` и ассоциативную таблицу `vacancy_skills` (связь «многие-ко-многим» между вакансиями и навыками). Схема создаётся и изменяется через миграции Alembic.

```mermaid
erDiagram
    CONTINENTS ||--o{ COUNTRIES : contains
    COUNTRIES ||--o{ VACANCIES : has
    COMPANIES ||--o{ VACANCIES : posts
    JOB_TITLES ||--o{ VACANCIES : defines
    SPECIALIZATIONS ||--o{ VACANCIES : classifies
    INDUSTRIES ||--o{ VACANCIES : belongs_to
    EMPLOYMENT_TYPES ||--o{ VACANCIES : defines
    CERTIFICATION_REQUIREMENTS o|--o{ VACANCIES : specifies
    VACANCIES ||--o{ VACANCY_SKILLS : requires
    SKILLS ||--o{ VACANCY_SKILLS : included_in

    CONTINENTS {
        int id PK
        string name UK
    }
    COUNTRIES {
        int id PK
        string name UK
        int continent_id FK
    }
    COMPANIES { int id PK string name UK }
    JOB_TITLES { int id PK string name UK }
    SPECIALIZATIONS { int id PK string name UK }
    INDUSTRIES { int id PK string name UK }
    EMPLOYMENT_TYPES { int id PK string name UK }
    CERTIFICATION_REQUIREMENTS { int id PK string name UK }
    SKILLS { int id PK string name UK }

    VACANCIES {
        int id PK
        string source_job_id UK
        int company_id FK
        int country_id FK
        int job_title_id FK
        int specialization_id FK
        int industry_id FK
        int employment_type_id FK
        int certification_requirement_id FK "nullable"
        string company_size "nullable"
        string education_required "nullable"
        string experience_level
        decimal years_of_experience "nullable"
        decimal salary_usd
        decimal salary_min "nullable"
        decimal salary_max "nullable"
        string salary_category "nullable"
        decimal bonus_percentage "nullable"
        bool equity_offered "nullable"
        decimal benefits_value_usd "nullable"
        int job_openings "nullable"
        int competition_level_applicants "nullable"
        decimal hiring_difficulty "nullable"
        bool work_from_home_available "nullable"
        decimal remote_work_percentage "nullable"
        decimal job_satisfaction "nullable"
        decimal work_life_balance "nullable"
        decimal ai_investment_company_millions "nullable"
        decimal company_ai_maturity "nullable"
        decimal job_growth_projection_percentage "nullable"
        decimal automation_risk_percentage "nullable"
        decimal gender_diversity_female_percentage "nullable"
        date posted_date
        date application_deadline "nullable"
        date record_created
        string data_source
    }

    VACANCY_SKILLS {
        int id PK
        int vacancy_id FK
        int skill_id FK
        "UK(vacancy_id, skill_id)"
    }
```

## Краткое описание

- **Связи 1:N**: `continents→countries`, справочники (company, country, job_title, specialization, industry, employment_type, certification_requirement) → `vacancies`.
- **Связь M:N**: `vacancies ↔ skills` через `vacancy_skills` (уникальная пара вакансия-навык, каскадное удаление).
- **Ограничения целостности**: PK/FK, `UNIQUE` (`source_job_id`, имена справочников, пары в `vacancy_skills`), `NOT NULL` для ключевых полей, `CHECK` (диапазоны зарплат/процентов/рейтингов, неотрицательные значения, дедлайн не раньше публикации).
- **Индексы**: внешние ключи и часто используемые поля поиска/фильтрации индексируются миграциями.
