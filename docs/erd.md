# ER-диаграмма базы данных

База данных состоит из 11 таблиц. Справочники хранят повторно используемые значения, таблица `vacancies` содержит
сведения о вакансиях, а `vacancy_skills` реализует связь многие-ко-многим между вакансиями и навыками.

```mermaid
erDiagram
    CONTINENTS ||--o{ COUNTRIES: contains
    COUNTRIES ||--o{ VACANCIES: has
    COMPANIES ||--o{ VACANCIES: posts
    JOB_TITLES ||--o{ VACANCIES: defines
    SPECIALIZATIONS ||--o{ VACANCIES: classifies
    INDUSTRIES ||--o{ VACANCIES: belongs_to
    EMPLOYMENT_TYPES ||--o{ VACANCIES: defines
    CERTIFICATION_REQUIREMENTS o|--o{ VACANCIES: specifies
    VACANCIES ||--o{ VACANCY_SKILLS: requires
    SKILLS ||--o{ VACANCY_SKILLS: included_in

    CONTINENTS {
        int id PK
        string name UK
    }

    COUNTRIES {
        int id PK
        string name UK
        int continent_id FK
    }

    COMPANIES {
        int id PK
        string name UK
    }

    JOB_TITLES {
        int id PK
        string name UK
    }

    SPECIALIZATIONS {
        int id PK
        string name UK
    }

    INDUSTRIES {
        int id PK
        string name UK
    }

    EMPLOYMENT_TYPES {
        int id PK
        string name UK
    }

    CERTIFICATION_REQUIREMENTS {
        int id PK
        string name UK
    }

    SKILLS {
        int id PK
        string name UK
    }

    VACANCIES {
        int id PK
        string source_job_id UK
        int company_id FK
        int country_id FK
        int job_title_id FK
        int specialization_id FK
        int industry_id FK
        int employment_type_id FK
        int certification_requirement_id FK
        decimal salary_usd
        date posted_date
    }

    VACANCY_SKILLS {
        int id PK
        int vacancy_id FK
        int skill_id FK
    }
```
