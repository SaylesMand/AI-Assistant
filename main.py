from crawler import BaseCrawler
from time import time


url = "https://help.ptsecurity.com/ru-RU/projects/mp10/27.4/help/922069771"
base_crawler = BaseCrawler(url=url)

start = time()
base_crawler.run_crawler(url, max_depth=0, max_concurrent=5)
end = time()
print(f"\nПрошло {end - start:.2f} секунд\n")
