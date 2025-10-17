import re
import json
from typing import Optional
from urllib.parse import urlparse
from functools import wraps

import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


class BaseCrawler:
    def __init__(self, url):
        self.url = url
        parsed_url = urlparse(url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self._base_domain = parsed_url.netloc

    def _clean_text(self, text: str) -> str:
        # Удаляем soft hyphen, zero-width space, no-break space, etc.
        return re.sub(r"[\u00AD\u200B\uFEFF\u2060\u00A0]", "", text)

    def _clean_title(self, text: str) -> str:
        "· MaxPatrol10 · Справочный портал"
        return re.sub(r"[\u00AD\u200B\uFEFF\u2060\u00A0]", " ", text).replace(
            " · MaxPatrol 10 · Справочный портал", ""
        )

    def _build_run_config(self, **kwargs) -> CrawlerRunConfig:
        """Создание конфигурации для crawler"""
        default_config = {
            "cache_mode": CacheMode.BYPASS,
            "wait_for": """
                () => {
                    const container = document.querySelector('content-container');
                    if (!container) return false;
                    const text = container.innerText || '';
                    return text.trim().length > 100;
                }
            """,
            "excluded_selector": "footer",
            "exclude_all_images": True,
        }

        config = {**default_config, **kwargs}

        return CrawlerRunConfig(**config)

    def retry_async(retries: int = 2, delay: float = 1.5):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                for attempt in range(1, retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        print(
                            f"[Attempt {attempt}/{retries}] {func.__name__} failed: {e}"
                        )
                        if attempt < retries:
                            await asyncio.sleep(delay)
                        else:
                            return

            return wrapper

        return decorator

    @retry_async(retries=2, delay=1.5)
    async def _fetch_page_data(
        self, crawler, url: str, semaphore: asyncio.Semaphore, retries: int = 2
    ):
        """Асинхронное извлечение ссылок и содержимого с повторной попыткой и ограничением параллелизма"""
        run_config1 = self._build_run_config()
        run_config2 = self._build_run_config(
            css_selector="content-container",
        )

        async with semaphore:  # ограничение числа одновременных запросов            
            result1, result2 = await asyncio.gather(
                crawler.arun(url=url, config=run_config1),
                crawler.arun(url=url, config=run_config2),
            )

        return {
            "url": result1.url,
            "title": self._clean_title(result1.metadata.get("title", "Без заголовка")),
            "content": self._clean_text(result2.markdown.raw_markdown),
            "internal_links": result1.links["internal"],
            "external_links": result1.links["external"],
        }

    def _normalize_link(self, link: str) -> Optional[str]:
        """Исправляет ссылку, если нужно, и фильтрует ненужные"""
        if len(link["text"]) > 0 and "cookie" not in link["href"]:
            if self._base_domain not in link["href"]:
                link["href"] = self.base_url + link["href"]
            return link["href"]
        return None

    async def _crawl_all_pages(
        self, start_url: str, max_depth: int = 3, max_concurrent: int = 5
    ) -> dict[str, dict]:
        """Асинхронный BFS-обход всех ссылок до указанной глубины"""
        visited: set[str] = set()
        found: set[str] = set()
        data: dict[str, dict] = dict()
        queue: list[tuple[str, int]] = [(start_url, 0)]

        semaphore = asyncio.Semaphore(max_concurrent)
        browser_conf = BrowserConfig(verbose=False)

        async with AsyncWebCrawler(config=browser_conf) as crawler:
            while queue:
                # Берём все ссылки текущего уровня
                current_batch = [item for item in queue if item[1] <= max_depth]
                queue = []  # очистим очередь для следующего уровня

                tasks = [
                    self._fetch_page_data(crawler, url, semaphore)
                    for url, _ in current_batch
                    if url not in visited
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for (url, depth), res in zip(current_batch, results):
                    if isinstance(res, Exception):
                        print(f"Error fetching {url}: {res}")
                        continue

                    visited.add(url)
                    data[url] = {
                        "title": res["title"],
                        "content": res["content"],
                    }

                    all_links = res.get("internal_links", []) + res.get(
                        "external_links", []
                    )
                    for link in all_links:
                        corrected = self._normalize_link(link)
                        if (
                            corrected
                            and corrected not in visited
                            and corrected not in found
                        ):
                            found.add(corrected)

                            if depth + 1 <= max_depth:
                                queue.append((corrected, depth + 1))

        return data

    def run_crawler(self, start_url: str, max_depth: int = 2, max_concurrent: int = 5):
        """Синхронная обёртка над асинхронным BFS-обходом"""
        data = asyncio.run(self._crawl_all_pages(start_url, max_depth, max_concurrent))

        with open("data.json", "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False)
        print(f"{len(data)} страниц сохранено в data.json")
