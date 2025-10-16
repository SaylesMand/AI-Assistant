import re
import json
from time import time


import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


def clean_text(text: str) -> str:
    # Удаляем soft hyphen, zero-width space, no-break space, etc.
    return re.sub(r"[\u00AD\u200B\uFEFF\u2060\u00A0]", "", text)


async def fetch_page_data(
    crawler, url: str, semaphore: asyncio.Semaphore, retries: int = 2
):
    """Асинхронное извлечение ссылок и содержимого с повторной попыткой и ограничением параллелизма"""
    run_conf1 = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_for="""
        () => {
            const container = document.querySelector('content-container');
            if (!container) return false;
            const text = container.innerText || '';
            return text.trim().length > 100;
        }
        """,
        excluded_selector="footer",
    )

    run_conf2 = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_for="""
        () => {
            const container = document.querySelector('content-container');
            if (!container) return false;
            const text = container.innerText || '';
            return text.trim().length > 100;
        }
        """,
        excluded_selector="footer",
        css_selector="content-container",
        only_text=True,
        exclude_all_images=True,
    )
    async with semaphore:  # ограничение числа одновременных запросов
        for attempt in range(1, retries + 1):
            try:
                result1 = await crawler.arun(url=url, config=run_conf1)
                result2 = await crawler.arun(url=url, config=run_conf2)

                return {
                    "url": result1.url,
                    "title": result1.metadata.get("title", "No title").replace(
                        " · MaxPatrol 10 · Справочный портал", ""
                    ),
                    "content": clean_text(result2.markdown.raw_markdown),
                    "internal_links": result1.links["internal"],
                    "external_links": result1.links["external"],
                }
            except Exception as e:
                print(f"[Attempt {attempt}/{retries}] Failed to fetch {url}: {e}")
                if attempt == retries:
                    return {
                        "url": "",
                        "title": "No title",
                        "content": "",
                        "internal_links": [],
                        "external_links": [],
                    }
                await asyncio.sleep(1.5)


def normalize_link(link, base_url):
    """Исправляет ссылку, если нужно, и фильтрует ненужные"""
    if len(link["text"]) > 0 and "cookie" not in link["href"]:
        if "ptsecurity.com" not in link["href"]:
            link["href"] = base_url + link["href"]
        return link["href"]
    return None


async def crawl_all_pages(
    base_url: str, start_url: str, max_depth: int = 3, max_concurrent: int = 5
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
                fetch_page_data(crawler, url, semaphore)
                for url, _ in current_batch
                if url not in visited
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for (url, depth), res in zip(current_batch, results):
                if isinstance(res, Exception):
                    print(f"Error fetching {url}: {res}")
                    continue

                visited.add(url)

                all_links = res.get("internal_links", []) + res.get(
                    "external_links", []
                )
                for link in all_links:
                    corrected = normalize_link(link, base_url)
                    if (
                        corrected
                        and corrected not in visited
                        and corrected not in found
                    ):
                        found.add(corrected)
                        data[url] = {
                            "title": res["title"],
                            "content": res["content"],
                            "links": corrected,
                        }

                        if depth + 1 <= max_depth:
                            queue.append((corrected, depth + 1))

    return data


def run_crawler(
    base_url: str, start_url: str, max_depth: int = 3, max_concurrent: int = 5
) -> list[str]:
    """Синхронная обёртка над асинхронным BFS-обходом"""
    return asyncio.run(crawl_all_pages(base_url, start_url, max_depth, max_concurrent))


base_url = "https://help.ptsecurity.com"
url = "https://help.ptsecurity.com/ru-RU/projects/mp10/27.4/help/93816075"

start_time = time()
data = run_crawler(base_url, url, max_depth=2, max_concurrent=5)
end_time = time()

print(f"\nПрошло: {end_time - start_time:.2f} секунд\n")


with open("data.json", "w", encoding="utf-8") as fp:
    json.dump(data, fp, ensure_ascii=False)

print(f"{len(data)} pages saved to data.json")
