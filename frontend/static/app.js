const API_URL = "/api/v1";
const PAGE_SIZE = 20;

const vacanciesTable = document.getElementById("vacancies-table");
const vacancyForm = document.getElementById("vacancy-form");
const formPanel = document.getElementById("vacancy-form-panel");
const formTitle = document.getElementById("form-title");
const saveButton = document.getElementById("save-vacancy-button");
const formMessage = document.getElementById("form-message");

const defaultSaveButtonText = saveButton.textContent;

let currentPage = 1;
let totalVacancies = 0;
let editingVacancyId = null;

let referenceData = {
    companies: [],
    jobTitles: [],
    countries: [],
    specializations: [],
    industries: [],
    employmentTypes: [],
    skills: [],
};

let selectedSkills = new Map();
let selectedVacancies = new Set();


// --------------------------------------------------
// API
// --------------------------------------------------

async function apiRequest(url, options = {}) {
    const { meta = false, headers: extraHeaders, ...fetchOptions } = options;
    const response = await fetch(`${API_URL}${url}`, {
        headers: {
            "Content-Type": "application/json",
            ...extraHeaders,
        },
        ...fetchOptions,
    });

    if (response.status === 204) {
        return meta ? { data: null, response } : null;
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        let message = "Произошла ошибка при обращении к серверу.";

        if (typeof data?.detail === "string") {
            message = data.detail;
        } else if (Array.isArray(data?.detail)) {
            message = data.detail
                .map((item) => item.msg || JSON.stringify(item))
                .join("; ");
        } else if (typeof data?.message === "string") {
            message = data.message;
        } else if (data?.detail) {
            message = JSON.stringify(data.detail);
        }

        throw new Error(message);
    }

    return meta ? { data, response } : data;
}


// --------------------------------------------------
// Сообщения
// --------------------------------------------------

function showToast(message, isError = false) {
    const toast = document.createElement("div");

    toast.className = isError ? "toast error" : "toast";
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3500);
}


function showFormMessage(message, isError = true) {
    formMessage.textContent = message;
    formMessage.hidden = false;
    formMessage.classList.toggle("error", isError);
}


function hideFormMessage() {
    formMessage.textContent = "";
    formMessage.hidden = true;
}


// --------------------------------------------------
// Форматирование
// --------------------------------------------------

function formatSalary(value) {
    if (value === null || value === undefined) {
        return "—";
    }

    return new Intl.NumberFormat("ru-RU", {
        maximumFractionDigits: 0,
    }).format(Number(value));
}


function formatDate(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleDateString("ru-RU");
}


function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (character) => {
        const characters = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;",
        };

        return characters[character];
    });
}


// --------------------------------------------------
// Справочники
// --------------------------------------------------

function getReferenceName(item) {
    return (
        item.name ??
        item.title ??
        item.skill_name ??
        item.company_name ??
        item.job_title ??
        String(item.id)
    );
}


async function loadReference(endpoint, selectId, placeholder) {
    const items = await apiRequest(endpoint);

    const select = document.getElementById(selectId);

    select.innerHTML = "";

    const firstOption = document.createElement("option");
    firstOption.value = "";
    firstOption.textContent = placeholder;

    select.appendChild(firstOption);

    items.forEach((item) => {
        const option = document.createElement("option");

        option.value = item.id;
        option.textContent = getReferenceName(item);

        select.appendChild(option);
    });

    return items;
}


async function loadReferenceData() {
    const [
        companies,
        jobTitles,
        countries,
        specializations,
        industries,
        employmentTypes,
        skills,
    ] = await Promise.all([
        apiRequest("/companies"),
        apiRequest("/job-titles"),
        apiRequest("/countries"),
        apiRequest("/specializations"),
        apiRequest("/industries"),
        apiRequest("/employment-types"),
        apiRequest("/skills"),
    ]);

    referenceData = {
        companies,
        jobTitles,
        countries,
        specializations,
        industries,
        employmentTypes,
        skills,
    };

    fillSelect("company-select", companies, "Выберите компанию");
    fillSelect("job-title-select", jobTitles, "Выберите должность");
    fillSelect("country-select", countries, "Выберите страну");
    fillSelect(
        "specialization-select",
        specializations,
        "Выберите специализацию",
    );
    fillSelect("industry-select", industries, "Выберите отрасль");
    fillSelect(
        "employment-type-select",
        employmentTypes,
        "Выберите тип занятости",
    );

    fillSelect(
        "specialization-filter",
        specializations,
        "Все специализации",
        true,
    );

    renderSkillOptions();
}


function fillSelect(selectId, items, placeholder, keepFirstOption = false) {
    const select = document.getElementById(selectId);

    select.innerHTML = "";

    const firstOption = document.createElement("option");
    firstOption.value = "";
    firstOption.textContent = placeholder;

    select.appendChild(firstOption);

    items.forEach((item) => {
        const option = document.createElement("option");

        option.value = item.id;
        option.textContent = getReferenceName(item);

        select.appendChild(option);
    });
}


// --------------------------------------------------
// Аналитика
// --------------------------------------------------

async function loadAnalytics() {
    try {
        const data = await apiRequest("/analytics/summary");

        document.getElementById("total-vacancies").textContent =
            formatSalary(data.total_vacancies);

        document.getElementById("average-salary").textContent =
            data.average_salary === null
                ? "—"
                : `${formatSalary(data.average_salary)} $`;

        document.getElementById("countries-count").textContent =
            formatSalary(data.countries_count);

        document.getElementById("specializations-count").textContent =
            formatSalary(data.specializations_count);
    } catch (error) {
        console.error("Ошибка загрузки аналитики:", error);
    }
}


// --------------------------------------------------
// Вакансии: список и фильтры
// --------------------------------------------------

function getReferenceLabel(items, id) {
    const item = items.find((entry) => Number(entry.id) === Number(id));

    return item ? getReferenceName(item) : "—";
}


function getVacancyLabel(vacancy, field, referenceItems) {
    const possibleNames = {
        job_title_id: ["job_title_name", "job_title"],
        company_id: ["company_name", "company"],
        country_id: ["country_name", "country"],
        specialization_id: ["specialization_name", "specialization"],
    };

    for (const name of possibleNames[field] || []) {
        if (vacancy[name] && typeof vacancy[name] === "string") {
            return vacancy[name];
        }
    }

    return getReferenceLabel(referenceItems, vacancy[field]);
}


function getVacancyList(data, response) {
    if (Array.isArray(data)) {
        const headerTotal = response?.headers?.get("X-Total-Count");
        const total = headerTotal !== null && headerTotal !== undefined
            ? Number(headerTotal)
            : data.length;
        return {
            items: data,
            total: Number.isFinite(total) ? total : data.length,
        };
    }

    return {
        items: data.items ?? data.vacancies ?? data.results ?? [],
        total: data.total ?? data.total_count ?? 0,
    };
}


async function loadVacancies() {
    vacanciesTable.innerHTML = `
        <tr>
            <td colspan="8" class="empty-state">
                Загрузка вакансий...
            </td>
        </tr>
    `;

    try {
        const params = new URLSearchParams({
            offset: String((currentPage - 1) * PAGE_SIZE),
            limit: String(PAGE_SIZE),
            sort_by: "posted_date",
            sort_order: "asc",
        });

        const search = document.getElementById("search-input").value.trim();
        const specializationId =
            document.getElementById("specialization-filter").value;
        const minSalary =
            document.getElementById("salary-min-filter").value;
        const maxSalary =
            document.getElementById("salary-max-filter").value;

        if (search) {
            params.set("search", search);
        }

        if (specializationId) {
            params.set("specialization_id", specializationId);
        }

        if (minSalary) {
            params.set("min_salary", minSalary);
        }

        if (maxSalary) {
            params.set("max_salary", maxSalary);
        }

        const { data, response } = await apiRequest(
            `/vacancies?${params.toString()}`,
            { meta: true },
        );
        const result = getVacancyList(data, response);

        totalVacancies = result.total;
        renderVacancies(result.items);
        updatePagination();
    } catch (error) {
        console.error("Ошибка загрузки вакансий:", error);

        vacanciesTable.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    Не удалось загрузить вакансии.
                </td>
            </tr>
        `;

        showToast(error.message, true);
    }
}


function renderVacancies(vacancies) {
    if (!vacancies.length) {
        vacanciesTable.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    Вакансии не найдены по текущим условиям.
                </td>
            </tr>
        `;

        updateCompareButton();
        return;
    }

    vacanciesTable.innerHTML = vacancies.map((vacancy) => {
        const id = Number(vacancy.id);

        const title = getVacancyLabel(
            vacancy,
            "job_title_id",
            referenceData.jobTitles,
        );

        const company = getVacancyLabel(
            vacancy,
            "company_id",
            referenceData.companies,
        );

        const country = getVacancyLabel(
            vacancy,
            "country_id",
            referenceData.countries,
        );

        const specialization = getVacancyLabel(
            vacancy,
            "specialization_id",
            referenceData.specializations,
        );

        return `
            <tr>
                <td>
                    <input
                        type="checkbox"
                        class="compare-checkbox"
                        data-id="${id}"
                        ${selectedVacancies.has(id) ? "checked" : ""}
                        aria-label="Выбрать вакансию для сравнения"
                    >
                </td>

                <td>${escapeHtml(title)}</td>
                <td>${escapeHtml(company)}</td>
                <td>${escapeHtml(country)}</td>
                <td>${escapeHtml(specialization)}</td>
                <td>${escapeHtml(formatDate(vacancy.posted_date))}</td>
                <td>${escapeHtml(formatSalary(vacancy.salary_usd))}</td>

                <td>
                    <div class="table-actions">
                        <button
                            type="button"
                            class="button button-secondary edit-button"
                            data-id="${id}"
                        >
                            Изменить
                        </button>

                        <button
                            type="button"
                            class="button button-secondary delete-button"
                            data-id="${id}"
                        >
                            Удалить
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");

    updateCompareButton();
}


function updatePagination() {
    const totalPages = Math.max(1, Math.ceil(totalVacancies / PAGE_SIZE));

    document.getElementById("page-info").textContent =
        `Страница ${currentPage} из ${totalPages} · всего ${totalVacancies}`;

    const atStart = currentPage <= 1;
    const atEnd = currentPage >= totalPages;

    document.getElementById("first-page").disabled = atStart;
    document.getElementById("previous-page").disabled = atStart;
    document.getElementById("next-page").disabled = atEnd;
    document.getElementById("last-page").disabled = atEnd;
}


// --------------------------------------------------
// Выбор вакансий для сравнения
// --------------------------------------------------

function updateCompareButton() {
    const button = document.getElementById("compare-button");
    const clearButton = document.getElementById("clear-selection-button");

    button.disabled =
        selectedVacancies.size < 2 || selectedVacancies.size > 5;

    button.textContent = selectedVacancies.size
        ? `Сравнить выбранные (${selectedVacancies.size})`
        : "Сравнить выбранные";

    if (clearButton) {
        clearButton.hidden = selectedVacancies.size === 0;
    }
}

function syncComparisonCheckboxes() {
    document.querySelectorAll(".compare-checkbox").forEach((checkbox) => {
        checkbox.checked = selectedVacancies.has(Number(checkbox.dataset.id));
    });
}

function clearSelection() {
    selectedVacancies.clear();
    updateCompareButton();
    syncComparisonCheckboxes();
}

function resetFilters() {
    document.getElementById("search-input").value = "";
    document.getElementById("specialization-filter").value = "";
    document.getElementById("salary-min-filter").value = "";
    document.getElementById("salary-max-filter").value = "";
    currentPage = 1;
    clearSelection();
    document.getElementById("comparison-panel").hidden = true;
    loadVacancies();
}


vacanciesTable.addEventListener("change", (event) => {
    if (!event.target.classList.contains("compare-checkbox")) {
        return;
    }

    const vacancyId = Number(event.target.dataset.id);

    if (event.target.checked) {
        if (selectedVacancies.size >= 5) {
            event.target.checked = false;
            showToast("Можно сравнить не более 5 вакансий.", true);
            return;
        }

        selectedVacancies.add(vacancyId);
    } else {
        selectedVacancies.delete(vacancyId);
    }

    updateCompareButton();
    refreshComparison();
});


async function compareVacancies() {
    if (selectedVacancies.size < 2 || selectedVacancies.size > 5) {
        showToast("Выберите от 2 до 5 вакансий.", true);
        return;
    }

    document.getElementById("comparison-panel").hidden = false;
    await refreshComparison();
    document.getElementById("comparison-panel").scrollIntoView({
        behavior: "smooth",
    });
}

async function refreshComparison() {
    const panel = document.getElementById("comparison-panel");
    const container = document.getElementById("comparison-result");

    if (panel.hidden) {
        return;
    }

    if (selectedVacancies.size < 2) {
        container.innerHTML = `
            <p class="empty-state">Для сравнения нужно минимум 2 вакансии. Добавьте ещё из списка или закройте окно.</p>
        `;
        return;
    }

    try {
        const result = await apiRequest("/vacancies/compare", {
            method: "POST",
            body: JSON.stringify({
                vacancy_ids: Array.from(selectedVacancies),
            }),
        });
        renderComparison(result);
    } catch (error) {
        container.innerHTML = `
            <p class="empty-state">Не удалось обновить сравнение.</p>
        `;
        showToast(error.message, true);
    }
}


function renderComparison(result) {
    const container = document.getElementById("comparison-result");
    const vacancies = result.vacancies || [];

    if (vacancies.length < 2) {
        container.innerHTML = `
            <p class="empty-state">Для сравнения нужно выбрать минимум 2 вакансии.</p>
        `;
        return;
    }

    const rows = vacancies.map((vacancy) => {
        const id = Number(vacancy.id);
        const title = getVacancyLabel(
            vacancy,
            "job_title_id",
            referenceData.jobTitles,
        );
        const company = getVacancyLabel(
            vacancy,
            "company_id",
            referenceData.companies,
        );

        return `
            <tr>
                <td>
                    <input
                        type="checkbox"
                        class="comparison-toggle"
                        data-id="${id}"
                        checked
                        aria-label="Включить вакансию в сравнение"
                    >
                </td>
                <td>${escapeHtml(title)}</td>
                <td>${escapeHtml(company)}</td>
                <td>${escapeHtml(formatSalary(vacancy.salary_usd))} $</td>
            </tr>
        `;
    }).join("");

    const highestVacancy = vacancies.find(
        (vacancy) => Number(vacancy.id) === Number(result.highest_paid_vacancy_id),
    );
    const lowestVacancy = vacancies.find(
        (vacancy) => Number(vacancy.id) === Number(result.lowest_paid_vacancy_id),
    );

    const formatCompared = (vacancy) => {
        if (!vacancy) {
            return "—";
        }
        const title = getVacancyLabel(
            vacancy,
            "job_title_id",
            referenceData.jobTitles,
        );
        const company = getVacancyLabel(
            vacancy,
            "company_id",
            referenceData.companies,
        );
        return `${formatSalary(vacancy.salary_usd)} $ (${title}, ${company})`;
    };

    container.innerHTML = `
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>В сравнении</th>
                        <th>Должность</th>
                        <th>Компания</th>
                        <th>Зарплата, USD</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        </div>

        <div class="comparison-summary">
            <p><strong>Средняя зарплата:</strong> ${escapeHtml(formatSalary(result.average_salary))} $</p>
            <p><strong>Разница между зарплатами:</strong> ${escapeHtml(formatSalary(result.salary_difference))} $</p>
            <p><strong>Самая высокая зарплата:</strong> ${escapeHtml(formatCompared(highestVacancy))}</p>
            <p><strong>Самая низкая зарплата:</strong> ${escapeHtml(formatCompared(lowestVacancy))}</p>
        </div>
    `;
}


// --------------------------------------------------
// Навыки
// --------------------------------------------------

function renderSkillOptions(searchText = "") {
    const container = document.getElementById("skill-options");
    const normalizedSearch = searchText.trim().toLowerCase();

    const filteredSkills = referenceData.skills.filter((skill) =>
        getReferenceName(skill).toLowerCase().includes(normalizedSearch),
    );

    if (!filteredSkills.length) {
        container.innerHTML = `
            <p class="empty-state">Навыки не найдены.</p>
        `;
        return;
    }

    container.innerHTML = filteredSkills.map((skill) => {
        const checked = selectedSkills.has(Number(skill.id));

        return `
            <label class="skill-option">
                <input
                    type="checkbox"
                    class="skill-checkbox"
                    value="${skill.id}"
                    ${checked ? "checked" : ""}
                >
                <span>${escapeHtml(getReferenceName(skill))}</span>
            </label>
        `;
    }).join("");
}


function renderSelectedSkills() {
    const container = document.getElementById("selected-skills");

    if (!selectedSkills.size) {
        container.innerHTML = `
            <span class="selected-skills-placeholder">
                Навыки пока не выбраны
            </span>
        `;
        return;
    }

    container.innerHTML = Array.from(selectedSkills.entries())
        .map(([id, name]) => `
            <span class="skill-tag">
                ${escapeHtml(name)}
                <button
                    type="button"
                    class="remove-skill-button"
                    data-id="${id}"
                    aria-label="Удалить навык"
                >
                    ×
                </button>
            </span>
        `)
        .join("");
}


function setSelectedSkills(skillIds) {
    selectedSkills.clear();

    skillIds.forEach((id) => {
        const skill = referenceData.skills.find(
            (item) => Number(item.id) === Number(id),
        );

        if (skill) {
            selectedSkills.set(
                Number(skill.id),
                getReferenceName(skill),
            );
        }
    });

    renderSkillOptions(
        document.getElementById("skill-search").value,
    );

    renderSelectedSkills();
}


function resetSkills() {
    selectedSkills.clear();

    document.getElementById("skill-search").value = "";
    renderSkillOptions();
    renderSelectedSkills();
}


document.getElementById("skill-options").addEventListener(
    "change",
    (event) => {
        if (!event.target.classList.contains("skill-checkbox")) {
            return;
        }

        const id = Number(event.target.value);

        const skill = referenceData.skills.find(
            (item) => Number(item.id) === id,
        );

        if (!skill) {
            return;
        }

        if (event.target.checked) {
            selectedSkills.set(id, getReferenceName(skill));
        } else {
            selectedSkills.delete(id);
        }

        renderSelectedSkills();
    },
);


document.getElementById("selected-skills").addEventListener(
    "click",
    (event) => {
        const button = event.target.closest(".remove-skill-button");

        if (!button) {
            return;
        }

        selectedSkills.delete(Number(button.dataset.id));

        renderSkillOptions(
            document.getElementById("skill-search").value,
        );

        renderSelectedSkills();
    },
);


document.getElementById("skill-search").addEventListener(
    "input",
    (event) => {
        renderSkillOptions(event.target.value);
    },
);


document.getElementById("skill-picker-button").addEventListener(
    "click",
    () => {
        const list = document.getElementById("skill-picker-list");
        const button = document.getElementById("skill-picker-button");

        list.hidden = !list.hidden;

        button.setAttribute("aria-expanded", String(!list.hidden));
    },
);


// --------------------------------------------------
// Форма: открытие и закрытие
// --------------------------------------------------

function openVacancyForm() {
    editingVacancyId = null;

    vacancyForm.reset();
    resetSkills();
    hideFormMessage();

    formTitle.textContent = "Новая вакансия";
    saveButton.textContent = defaultSaveButtonText;

    document.getElementById("skill-picker-list").hidden = true;
    document.getElementById("skill-picker-button").setAttribute(
        "aria-expanded",
        "false",
    );

    formPanel.hidden = false;

    formPanel.scrollIntoView({
        behavior: "smooth",
    });
}


function closeVacancyForm() {
    formPanel.hidden = true;

    vacancyForm.reset();
    resetSkills();
    hideFormMessage();

    editingVacancyId = null;
    formTitle.textContent = "Новая вакансия";
    saveButton.textContent = defaultSaveButtonText;

    document.getElementById("skill-picker-list").hidden = true;
    document.getElementById("skill-picker-button").setAttribute(
        "aria-expanded",
        "false",
    );
}


// --------------------------------------------------
// Редактирование вакансии
// --------------------------------------------------

function setSelectValue(select, value) {
    if (value === null || value === undefined) {
        select.value = "";
        return;
    }

    const stringValue = String(value);

    let option = Array.from(select.options).find(
        (item) => item.value === stringValue,
    );

    // Если значение из базы отсутствует в вариантах формы,
    // добавляем его, чтобы не потерять исходную категорию опыта.
    if (!option) {
        option = document.createElement("option");
        option.value = stringValue;
        option.textContent = stringValue;
        select.appendChild(option);
    }

    select.value = stringValue;
}


async function openEditForm(vacancyId) {
    try {
        const vacancy = await apiRequest(`/vacancies/${vacancyId}`);

        editingVacancyId = vacancyId;

        vacancyForm.reset();
        hideFormMessage();

        setSelectValue(
            document.getElementById("company-select"),
            vacancy.company_id,
        );

        setSelectValue(
            document.getElementById("job-title-select"),
            vacancy.job_title_id,
        );

        setSelectValue(
            document.getElementById("country-select"),
            vacancy.country_id,
        );

        setSelectValue(
            document.getElementById("specialization-select"),
            vacancy.specialization_id,
        );

        setSelectValue(
            document.getElementById("industry-select"),
            vacancy.industry_id,
        );

        setSelectValue(
            document.getElementById("employment-type-select"),
            vacancy.employment_type_id,
        );

        setSelectValue(
            vacancyForm.elements["experience_level"],
            vacancy.experience_level,
        );

        vacancyForm.elements["salary_usd"].value =
            vacancy.salary_usd ?? "";

        setSelectedSkills(vacancy.skill_ids || []);

        formTitle.textContent = "Редактирование вакансии";
        saveButton.textContent = "Сохранить изменения";

        document.getElementById("skill-picker-list").hidden = true;

        formPanel.hidden = false;

        formPanel.scrollIntoView({
            behavior: "smooth",
        });
    } catch (error) {
        showToast(error.message, true);
    }
}


// --------------------------------------------------
// Удаление вакансии
// --------------------------------------------------

async function deleteVacancy(vacancyId) {
    const confirmed = confirm(
        "Вы действительно хотите удалить эту вакансию?",
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(`/vacancies/${vacancyId}`, {
            method: "DELETE",
        });

        selectedVacancies.delete(vacancyId);

        showToast("Вакансия удалена.");

        await loadVacancies();
        await loadAnalytics();
    } catch (error) {
        showToast(error.message, true);
    }
}


// --------------------------------------------------
// Создание и редактирование: отправка формы
// --------------------------------------------------

vacancyForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    hideFormMessage();

    const formData = new FormData(vacancyForm);

    const payload = {
        company_id: Number(formData.get("company_id")),
        job_title_id: Number(formData.get("job_title_id")),
        country_id: Number(formData.get("country_id")),
        specialization_id: Number(formData.get("specialization_id")),
        industry_id: Number(formData.get("industry_id")),
        employment_type_id: Number(formData.get("employment_type_id")),
        experience_level: formData.get("experience_level"),
        salary_usd: Number(formData.get("salary_usd")),
        skill_ids: Array.from(selectedSkills.keys()),
    };

    const isEditing = editingVacancyId !== null;

    saveButton.disabled = true;
    saveButton.textContent = "Сохранение...";

    try {
        if (isEditing) {
            await apiRequest(`/vacancies/${editingVacancyId}`, {
                method: "PATCH",
                body: JSON.stringify(payload),
            });

            showToast("Изменения сохранены.");
        } else {
            await apiRequest("/vacancies", {
                method: "POST",
                body: JSON.stringify(payload),
            });

            showToast("Вакансия успешно добавлена.");
        }

        closeVacancyForm();

        currentPage = 1;

        await loadVacancies();
        await loadAnalytics();
    } catch (error) {
        showFormMessage(error.message);
    } finally {
        saveButton.disabled = false;

        if (editingVacancyId !== null) {
            saveButton.textContent = "Сохранить изменения";
        } else {
            saveButton.textContent = defaultSaveButtonText;
        }
    }
});


// --------------------------------------------------
// Обработчики кнопок
// --------------------------------------------------

document.getElementById("add-vacancy-button").addEventListener(
    "click",
    openVacancyForm,
);


document.getElementById("cancel-form-button").addEventListener(
    "click",
    closeVacancyForm,
);


document.getElementById("filter-button").addEventListener(
    "click",
    () => {
        currentPage = 1;
        clearSelection();
        loadVacancies();
    },
);

document.getElementById("reset-filters-button").addEventListener(
    "click",
    resetFilters,
);

document.getElementById("clear-selection-button").addEventListener(
    "click",
    () => {
        clearSelection();
        document.getElementById("comparison-panel").hidden = true;
        showToast("Выбор вакансий сброшен.");
    },
);


document.getElementById("search-input").addEventListener(
    "keydown",
    (event) => {
        if (event.key === "Enter") {
            currentPage = 1;
            clearSelection();
            loadVacancies();
        }
    },
);


document.getElementById("first-page").addEventListener("click", () => {
    if (currentPage !== 1) {
        currentPage = 1;
        loadVacancies();
    }
});

document.getElementById("previous-page").addEventListener(
    "click",
    () => {
        if (currentPage > 1) {
            currentPage -= 1;
            loadVacancies();
        }
    },
);

document.getElementById("next-page").addEventListener(
    "click",
    () => {
        const totalPages = Math.ceil(totalVacancies / PAGE_SIZE);

        if (currentPage < totalPages) {
            currentPage += 1;
            loadVacancies();
        }
    },
);

document.getElementById("last-page").addEventListener("click", () => {
    const totalPages = Math.max(1, Math.ceil(totalVacancies / PAGE_SIZE));
    if (currentPage !== totalPages) {
        currentPage = totalPages;
        loadVacancies();
    }
});


document.getElementById("compare-button").addEventListener(
    "click",
    compareVacancies,
);


document.getElementById("close-comparison-button").addEventListener(
    "click",
    () => {
        document.getElementById("comparison-panel").hidden = true;
        clearSelection();
        showToast("Сравнение закрыто, выбор сброшен.");
    },
);

document.getElementById("comparison-result").addEventListener("change", (event) => {
    if (!event.target.classList.contains("comparison-toggle")) {
        return;
    }

    const vacancyId = Number(event.target.dataset.id);
    if (event.target.checked) {
        if (selectedVacancies.size >= 5) {
            event.target.checked = false;
            showToast("Можно сравнить не более 5 вакансий.", true);
            return;
        }
        selectedVacancies.add(vacancyId);
    } else {
        selectedVacancies.delete(vacancyId);
    }

    updateCompareButton();
    syncComparisonCheckboxes();
    refreshComparison();
});


// Делегирование событий для кнопок в строках таблицы.
vacanciesTable.addEventListener("click", async (event) => {
    const editButton = event.target.closest(".edit-button");
    const deleteButton = event.target.closest(".delete-button");

    if (editButton) {
        await openEditForm(Number(editButton.dataset.id));
    }

    if (deleteButton) {
        await deleteVacancy(Number(deleteButton.dataset.id));
    }
});


// --------------------------------------------------
// Запуск приложения
// --------------------------------------------------

async function initializeApp() {
    try {
        await loadReferenceData();

        await Promise.all([
            loadVacancies(),
            loadAnalytics(),
        ]);
    } catch (error) {
        console.error("Ошибка инициализации приложения:", error);
        showToast("Не удалось загрузить данные приложения.", true);
    }
}


initializeApp();
