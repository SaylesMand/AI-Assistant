import re
import asyncio

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


async def extract_links(url: str):
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
        exclude_external_links=False,
        excluded_selector="footer",
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_conf,
        )

        return {
            "internal_links": result.links["internal"],
            "external_links": result.links["external"],
        }


def get_correct_link(link, base_url):
    if len(link["text"]) > 0 and "cookie" not in link["href"]:
        if "ptsecurity.com" not in link["href"]:
            link["href"] = base_url + link["href"]
        return link["href"]
    return None


def get_correct_links(base_url, url):
    links = asyncio.run(extract_links(url))
    urls = []

    for links in links.values():
        for link in links:
            url = get_correct_link(link, base_url)
            if url:
                urls.append(url)
    return urls


# base_url = "https://help.ptsecurity.com"
# url = "https://help.ptsecurity.com/ru-RU/projects/mp10/27.4/help/93816075"

# print(get_correct_links(base_url, url))
