# AI Assistant - Многофункциональный LLM-ассистент

**AI Assistant** - это модульный сервис на базе **FastAPI** и **LangChain**, который объединяет три интеллектуальных агента:

* **RAG** - для работы с внутренней документацией,
* **SQL Agent** - для извлечения структурированных данных из базы данных,
* **Web Agent** - для поиска информации в интернете.

Все они управляются центральным оркестратором - **Router Agent**, который анализирует пользовательский запрос и решает, какой инструмент использовать (или их комбинацию).

---

## Архитектура проекта

```
AI-Assistant/
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
├─ docker-compose.yml        # Сервисы: Crawler, FastAPI и Qdrant
├─ Dockerfile                # Образ для FastAPI приложения
├─ Dockerfile.crawler        # Образ для Crawler
├─ README.md                 # Документация проекта
└─ requirements.txt          # Python-зависимости
```

---

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/SaylesMand/AI-Assistant.git
cd ai-assistant
```

### 2. Создание `.env` файла
Linux / macOS / PowerShell:
```bash
cp .env.example .env
```
CMD:
```bash
copy .env.example .env
```

Заполни своими значениями:

```env
# LLM CONFIGURATION
API_KEY=YOUR_API_KEY
# mistral | openai | ollama | vllm
LLM_MODE=mistral
LLM_MODEL=YOUR_LLM_MODEL
EMBEDDING_MODEL=YOUR_EMBEDDING_MODEL

# RAG Agent SETTINGS
DATA_PATH=data/data.json

# CRAWLER
DOCS_URL=https://help.ptsecurity.com/ru-RU/projects/mp10/27.4/help/922069771
```
### 3. Сборка контейнеров

```bash
docker-compose --build -d
```

### 4. Парсинг документации через crawler
Если `data/data.json` отсутствует или устарел - запусти:
```bash
docker-compose run --rm crawler
```

### 5. Запуск основного сервиса

```bash
docker-compose up -d
```

После запуска доступны сервисы:

* FastAPI - [http://localhost:8000](http://localhost:8000)
* Qdrant - [http://localhost:6333](http://localhost:6333)

Важно: Индексация и инициализация агентов может занять время - проверь логи:
```bash
docker logs ai-assistant -f
```
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

   * если запрос о документации - использует **RAG**;
   * если запрос про базу данных - использует **SQL**;
   * если запрос внешний - использует **Web**;
   * если нужно - комбинирует результаты.
3. Агент может комбинировать результаты (например, SQL + RAG).
4. Ответ возвращается в JSON.

---

## Пример запроса

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
Ревью LLM-ассистента приведено в [review.md](review.md)
---


## Технологии

* **Python 3.12**
* **FastAPI**
* **LangChain**
* **crawl4ai**
* **Qdrant (векторное хранилище)**
* **MistralAI**
* **Docker / docker-compose**

---

## Планы по развитию

* [ ] Система оценки качества ответов
* [ ] UI интерфейс (например, Streamlit)
* [ ] Глубокий поиск (Deep Search)

---

## Автор

**Daniil M.**
ML Engineer
📧 [Telegram](https://t.me/daniil_domino)
💼 [GitHub Profile](https://github.com/SaylesMand)

---
