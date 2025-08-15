import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from googlesearch import search
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from urlextract import URLExtract
from fake_useragent import UserAgent

# ----- Global Configurations & Utilities -------------------------------------------------------
extractor = URLExtract()
ua = UserAgent()

FILTER_KEYWORDS = ['login', 'signin', 'signup', 'register', 'account', 'sign_in', 'log_in', 'cookies']
EXCLUDED_DOMAINS = ['facebook.com', 'X.com', 'instagram.com', 'pinterest.com', 'tumblr.com']

# ----- Core Scraping Functions -----------------------------------------------------------------
def get_search_results(query: str, num_results: int = 2) -> list[str]:
    print(f"Searching Google for: '{query}'...")
    try:
        urls = list(search(query, num_results=num_results))
        return urls
    except Exception as e:
        print(f"An error occurred during Google search: {e}")
        return []
    
# ----- Crawler Settings ------------------------------------------------------------------------
async def perform_deep_crawl(crawler: AsyncWebCrawler, url: str) -> dict:
    print(f"Starting deep crawl from: {url}...")
    run_config = CrawlerRunConfig(
        excluded_tags=['header', 'footer', 'img', 'video', 'script', 'style', 'iframe', 'nav'],
        exclude_domains=EXCLUDED_DOMAINS,
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=1,
            include_external=False
        )
    )
    scraped_data = {}
    try:
        results = await crawler.arun(url=url, config=run_config)
        for result_item in results:
            if result_item.success and result_item.markdown:
                scraped_data[result_item.url] = result_item.markdown
            else:
                print(f"Failed to crawl page: {result_item.url} with error: {result_item.error_message}")
    except Exception as e:
        print(f"An error occurred during deep crawl from {url}: {e}")
        return {}
    
    if scraped_data:
        return scraped_data
    else:
        print(f"Deep crawl from {url} returned no scraped content.")
        return {}

# ----- FastAPI Application ------------------------------------------------------------------
app = FastAPI()

class ScrapeRequest(BaseModel):
    query: str

@app.post("/scrape/")
async def scrape_data(request: ScrapeRequest):
    user_input = request.query
    if not user_input.strip():
        raise HTTPException(status_code=400, detail="Input query cannot be empty.")

    links = extractor.find_urls(user_input)[:4]
    text_parts_string = user_input
    for link in links:
        text_parts_string = text_parts_string.replace(link, '')
    
    input_text_as_sentence = text_parts_string.strip()
    
    has_text = bool(input_text_as_sentence)
    has_links = bool(links)
    data_dictionary = {}
    
    try:
        async with AsyncWebCrawler() as crawler:
            initial_urls_to_scrape = []
            if has_text and not has_links:
                initial_urls_to_scrape = get_search_results(input_text_as_sentence, num_results=2)
            elif has_links:
                initial_urls_to_scrape = links

            for url in initial_urls_to_scrape:
                if any(keyword in url.lower() for keyword in FILTER_KEYWORDS) or \
                   any(domain in url.lower() for domain in EXCLUDED_DOMAINS):
                    print(f"Skipping excluded URL: {url}")
                    continue

                browser_config = BrowserConfig(user_agent=ua.random)
                crawler.config = browser_config
                scraped_content = await perform_deep_crawl(crawler, url)
                data_dictionary.update(scraped_content)
    
        if has_text and has_links:
            data_dictionary["input_text_parts"] = input_text_as_sentence
        
        if not data_dictionary:
            return {"message": "No content was scraped."}

        return {"scraped_data": data_dictionary}
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")