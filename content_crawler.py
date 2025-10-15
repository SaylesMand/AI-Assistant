import re
import asyncio

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


def clean_text(text: str) -> str:
    # Удаляем soft hyphen, zero-width space, no-break space, etc.
    return re.sub(r"[\u00AD\u200B\uFEFF\u2060\u00A0]", "", text)


async def crawl_page(url: str):
    browser_conf = BrowserConfig(verbose=True)
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        # wait_for="js:() => document.readyState === 'complete'",
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
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_conf,
        )

        return {
            "url": result.url,
            "title": result.metadata.get("title", "No title"),
            "content": result.markdown.raw_markdown,
        }


def get_crawled_data(url):
    doc = asyncio.run(crawl_page(url))
    doc["content"] = clean_text(doc["content"])
    return doc


# url = "https://help.ptsecurity.com/ru-RU/projects/mp10/27.4/help/93816075"
# print(get_crawled_data(url))
