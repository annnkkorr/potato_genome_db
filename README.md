# 🥔 Potato Genome DB

Веб-приложение для управления базой данных геномов картофеля.  
Стек: **FastAPI · SQLAlchemy · SQLite · Pydantic v2 · Jinja2**

---

## Быстрый старт

```bash
# 1. Установить зависимости
git clone https://github.com/annnkkorr/potato_genome_db
# 2. Установить зависимости
uv sync

# 3. Если база данных уже существует — выполнить миграцию (один раз)
uv run python migrate.py

# 4. Запустить сервер
uv run uvicorn main:app --reload
```

---

## Схема базы данных

### Organism
| Поле | Тип | Описание |
|---|---|---|
| `genome_id` | TEXT PK | Уникальный идентификатор генома |
| `organism_name` | TEXT | Название организма |
| `ploidy_type` | TEXT | Плоидность (`diploid`, `tetraploid`, `hexaploid`) |
| `description` | TEXT | Описание |

### Genome_assembly
| Поле | Тип | Описание |
|---|---|---|
| `genome_id` | TEXT PK, FK → Organism | Идентификатор генома |
| `assembly_file` | TEXT | Имя файла сборки |
| `assembly_link` | TEXT | Ссылка для скачивания |
| `masked_file` | TEXT | Имя маскированного файла |
| `masked_link` | TEXT | Ссылка на маскированный файл |
| `softmasked_file` | TEXT | Имя мягко-маскированного файла |
| `softmasked_link` | TEXT | Ссылка на мягко-маскированный файл |
| `release_date` | TEXT | Дата публикации (хранится как `YYYY-MM-DD`) |

### Genome_annotation
| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER PK | Суррогатный ключ |
| `genome_id` | TEXT, FK → Organism | Идентификатор генома |
| `set_type` | TEXT | Тип набора: `hc`, `representative`, `working` |
| `gff3_file` / `gff3_link` | TEXT | GFF3-аннотация |
| `cdna_file` / `cdna_link` | TEXT | cDNA-последовательности |
| `cds_file` / `cds_link` | TEXT | CDS-последовательности |
| `pep_file` / `pep_link` | TEXT | Пептидные последовательности |

> Пара `(genome_id, set_type)` уникальна — на каждый геном может быть до трёх строк аннотаций (по одной на каждый тип набора).

Каскадное удаление и обновление включены для обеих дочерних таблиц.

---

## Страницы

| Страница | URL | Возможности |
|---|---|---|
| Организмы | `/organisms` | Фильтр по названию и плоидности; добавление, редактирование, удаление |
| Сборки | `/assemblies` | Фильтр по ID генома; сортировка по дате публикации ▲▼; добавление, редактирование, удаление |
| Аннотации | `/annotations` | Фильтр по ID генома и типу набора; добавление, редактирование, удаление |
| Общий вид | `/joined` | LEFT JOIN трёх таблиц; фильтр по названию организма и плоидности; сортировка по дате публикации ▲▼; редактирование и удаление аннотаций |

---