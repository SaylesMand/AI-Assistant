# AI Assistant — Многофункциональный LLM-ассистент

**AI Assistant** — это модульный сервис на базе **FastAPI** и **LangChain**, который объединяет три интеллектуальных агента:

* **RAG** — для работы с внутренней документацией,
* **SQL Agent** — для извлечения структурированных данных из базы данных,
* **Web Agent** — для поиска информации в интернете.

Все они управляются центральным оркестратором — **Router Agent**, который анализирует пользовательский запрос и решает, какой инструмент использовать (или их комбинацию).

---

## Архитектура проекта

```
ai-assistant/
├─ src/
│  ├─ main.py                # Точка входа FastAPI
│  ├─ config.py              # Конфигурация и загрузка переменных окружения
│  ├─ crawler.py             # Парсинг документации в JSON
│
│  ├─ agent_router/          # Главный оркестратор (Router Agent)
│  │  ├─ router_agent.py     # Агент, выбирающий между RAG / SQL / Web
│  │  ├─ tools/              # Инструменты для Router Agent
│  │  │  ├─ rag_tool.py      # Вызов RAG агента
│  │  │  ├─ sql_tool.py      # Вызов SQL агента
│  │  │  └─ web_tool.py      # Вызов Web-поиска
│
│  ├─ api/                   # FastAPI эндпоинты
│  │  ├─ routes.py           # Основные маршруты API
│  │  └─ schemas.py          # Pydantic-модели запросов/ответов
│
│  ├─ rag/                   # Retrieval-Augmented Generation (RAG)
│  │  ├─ __init__.py         # Загрузка и инициализация RAG агента
│  │  ├─ loader.py           # Чтение JSON и создание документов
│  │  ├─ splitter.py         # Разделение текста на чанки
│  │  ├─ indexing.py         # Хранение векторов в Qdrant
│  │  └─ agent.py            # Логика RAG агента
│
│  ├─ sql/                   # SQL Agent
│  │  ├─ __init__.py         # Загрузка и инициализация SQL агента
│  │  └─ agent.py            # Работа с базой данных через LangChain
│
│  ├─ utils/                 # Вспомогательные утилиты
│  │  ├─ models/             # Модели LLM и фабрика провайдеров
│  │  │  ├─ base.py          # Базовые классы для LLM
│  │  │  ├─ llm_factory.py   # Создание Chat/Embedding моделей
│  │  └─ utils.py            # Хелперы и утилитарные функции
│
├─ data/                     # Локальные данные (JSON, Qdrant, SQLite)
│
├─ .env.example              # Пример переменных окружения
├─ .dockerignore             # Исключения для Docker сборки
├─ docker-compose.yml         # Оркестрация FastAPI + Qdrant
├─ Dockerfile                # Образ для FastAPI приложения
├─ README.md                 # Документация проекта
└─ requirements.txt          # Python-зависимости
```

---

## Установка и запуск

### 1. Клонируй репозиторий

```bash
git clone https://github.com/SaylesMand/ai-assistant.git
cd ai-assistant
```

### 2. Создай `.env` файл на основе шаблона

```bash
cp .env.example .env
```

и укажи свои значения:

```env
MISTRAL_API_KEY=your_api_key_here
QDRANT_PATH=data/qdrant
QDRANT_COLLECTION=qdrant_rag
DB_PATH=data/database.db
```

### 4. Собери контейнеры

```bash
docker-compose build
```

### 5. Запусти сервис

```bash
docker-compose up -d
```

После запуска:

* FastAPI — [http://localhost:8000](http://localhost:8000)
* Qdrant — [http://localhost:6333](http://localhost:6333)

---

## Основные компоненты

| Компонент        | Назначение                                                  |
| ---------------- | ----------------------------------------------------------- |
| **Router Agent** | Определяет, какой инструмент использовать (RAG / SQL / Web) |
| **RAG Agent**    | Ищет ответы во внутренней документации (через Qdrant)       |
| **SQL Agent**    | Выполняет SQL-запросы к локальной БД                        |
| **Web Tool**     | Выполняет поиск информации в интернете                      |
| **Crawler**      | Скачивает и обрабатывает документацию в JSON                |
| **Qdrant**       | Векторное хранилище для RAG                                 |

---

## Как это работает

1. Пользователь отправляет запрос через API `/agent/ask`.
2. Router Agent анализирует текст и выбирает подходящий инструмент:

   * если запрос о документации — использует **RAG**;
   * если запрос про базу данных — использует **SQL**;
   * если запрос внешний — использует **Web**;
   * если нужно — комбинирует результаты.
3. Агент формирует ответ и возвращает его пользователю в JSON.

---

## Примеры запросов

### Запрос к оркестратору

```bash
curl -X POST "http://localhost:8000/agent/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Какая архитектура у MaxPatrol 10?"}'
```

Ответ:

```json
{
  "answer": "MaxPatrol 10 построена на модульной архитектуре с центральным компонентом MP 10 Core..."
}
```

---

## Технологии

* **Python 3.12**
* **FastAPI**
* **LangChain**
* **Qdrant (векторное хранилище)**
* **Mistral / Ollama / OpenAI (через фабрику моделей)**
* **Docker / docker-compose**

---

## Переменные окружения

| Переменная          | Описание                             | Пример                 |
| ------------------- | ------------------------------------ | ---------------------- |
| `MISTRAL_API_KEY`   | API ключ модели Mistral              | `your_mistral_api_key` |
| `QDRANT_PATH`       | Путь к локальному Qdrant-хранилищу   | `data/qdrant`          |
| `QDRANT_COLLECTION` | Имя коллекции                        | `qdrant_rag`           |
| `DB_PATH`           | Путь к SQLite базе данных            | `data/employees.db`    |
| `CHUNK_SIZE`        | Размер чанков при нарезке документов | `1000`                 |
| `TOP_K`             | Количество возвращаемых документов   | `5`                    |

---

## Планы по развитию

* [ ] Оценка качества
* [ ] UI интерфейс (например, Streamlit)
* [ ] Глубокий поиск (Deep Search)

---

## Автор

**Daniil M.**
ML Engineer
📧 [[telegram](https://t.me/daniil_domino)]
💼 [GitHub Profile](https://github.com/SaylesMand)

---
