import asyncio
import json
import os
import re
from urllib.parse import urlparse
from googlesearch import search
from collections import defaultdict
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from urlextract import URLExtract
from fake_useragent import UserAgent
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- Constants and Crawler Filters ---
extractor = URLExtract()
ua = UserAgent()

FILTER_KEYWORDS = ['login', 'signin', 'signup', 'register', 'account', 'sign_in', 'log_in', 'privacy', 'cookies']
EXCLUDED_DOMAINS = ['facebook.com', 'X.com', 'instagram.com', 'pinterest.com', 'tumblr.com']
IGNORE_EXTENSIONS = ['.zip', '.pdf', '.docx', '.xlsx', '.pptx', '.jpg', '.jpeg', '.png', '.gif', '.mp3', '.mp4', '.avi', '.mov']
TIMEOUT_SECONDS = 30 

# --- Helper functions ---
def get_search_results(query: str, num_results: int = 2) -> list[str]:
    """Performs a Google search and returns a list of URLs."""
    print(f"Searching Google for: '{query}'...")
    try:
        urls = list(search(query, num_results=num_results))
        return urls
    except Exception as e:
        print(f"An error occurred during Google search: {e}")
        return []

async def perform_crawl(url: str, user_agent: str) -> dict:
    """Performs a single crawl for a given URL with a specified user agent."""
    scraped_data = {}
    try:
        async with AsyncWebCrawler() as crawler:
            browser_config = BrowserConfig(user_agent=user_agent)
            print(f"Starting crawl from: {url} with user agent: {browser_config.user_agent}")

            run_config = CrawlerRunConfig(
                excluded_tags=['header', 'footer', 'img', 'video', 'script', 'style', 'iframe', 'nav'],
                exclude_domains=EXCLUDED_DOMAINS,
                deep_crawl_strategy=None
            )

            results = await crawler.arun(url=url, config=run_config, browser_config=browser_config)
            
            for result_item in results:
                if result_item.success and result_item.markdown:
                    scraped_data[result_item.url] = (result_item.markdown, browser_config.user_agent)
                else:
                    print(f"Failed to crawl page: {result_item.url} with error: {result_item.error_message}")
    except Exception as e:
        print(f"An error occurred during crawl from {url}: {e}")
        return {}
    
    if scraped_data:
        return scraped_data
    else:
        print(f"Crawl from {url} returned no scraped content.")
        return {}

# --- FastAPI Integration ---
app = FastAPI()

class QueryRequest(BaseModel):
    """Pydantic model for the incoming request body."""
    user_input: str

@app.post("/scrape")
async def scrape_endpoint(request: QueryRequest):
    """
    API endpoint to perform web scraping based on a user query or URLs.
    """
    user_input = request.user_input
    if not user_input.strip():
        raise HTTPException(status_code=400, detail="Input cannot be empty.")
    
    links = extractor.find_urls(user_input)[:4]
    text_parts_string = user_input
    for link in links:
        text_parts_string = text_parts_string.replace(link, '')
    
    input_text_as_sentence = text_parts_string.strip()
    
    has_text = bool(input_text_as_sentence)
    has_links = bool(links)
    data_dictionary = {}
    
    initial_urls_to_crawl = []
    if has_text and not has_links:
        search_query = input_text_as_sentence
        initial_urls_to_crawl = get_search_results(search_query, num_results=2)
    elif has_links:
        initial_urls_to_crawl = links

    # Step 1: Concurrently crawl all initial URLs, switching UA for new domains
    domain_user_agents = defaultdict(lambda: ua.random)
    initial_tasks = []
    for url in initial_urls_to_crawl:
        if any(url.lower().endswith(ext) for ext in IGNORE_EXTENSIONS): 
            print(f"Skipping file URL: {url}")
            continue
        if any(keyword in url.lower() for keyword in FILTER_KEYWORDS) or any(domain in url.lower() for domain in EXCLUDED_DOMAINS):
            print(f"Skipping excluded URL: {url}")
            continue
        
        domain = urlparse(url).netloc
        user_agent_to_use = domain_user_agents[domain]
        initial_tasks.append(asyncio.wait_for(perform_crawl(url, user_agent_to_use), timeout=TIMEOUT_SECONDS))

    initial_results = await asyncio.gather(*initial_tasks, return_exceptions=True)

    # Process results from the initial crawl
    for result in initial_results:
        if isinstance(result, dict) and result is not None:
            data_dictionary.update(result)
        elif isinstance(result, asyncio.TimeoutError):
            print("An initial crawl task timed out. Skipping this URL.")
        elif isinstance(result, Exception):
            print(f"An exception occurred: {result}")

    # Step 2: Extract nested links from initially crawled results
    # ***MODIFIED: Collect all links (internal & external) from initial crawl***
    nested_urls_to_crawl = set()
    initial_domains = [urlparse(url).netloc for url in initial_urls_to_crawl]

    for url, data in data_dictionary.items():
        if isinstance(data, tuple) and len(data) == 2:
            markdown_content, _ = data
            found_urls = extractor.find_urls(markdown_content)
            
            for found_url in found_urls:
                if (urlparse(found_url).netloc not in initial_domains) or (urlparse(found_url).netloc == urlparse(url).netloc):
                    if not any(keyword in found_url.lower() for keyword in FILTER_KEYWORDS) and not any(domain in found_url.lower() for domain in EXCLUDED_DOMAINS):
                        nested_urls_to_crawl.add(found_url)
    
    # Step 3: Crawl nested links, but only for one level
    # ***MODIFIED: Use a single-level crawl, no deeper crawling***
    print("Crawling nested links (including a single level of external links).")
    nested_tasks = []
    # Limit to the first 10 nested links
    for url in list(nested_urls_to_crawl)[:10]:
        if any(url.lower().endswith(ext) for ext in IGNORE_EXTENSIONS):
            print(f"Skipping nested file URL: {url}")
            continue

        domain = urlparse(url).netloc
        user_agent_to_use = domain_user_agents[domain]
        nested_tasks.append(asyncio.wait_for(perform_crawl(url, user_agent_to_use), timeout=TIMEOUT_SECONDS))

    nested_results = await asyncio.gather(*nested_tasks, return_exceptions=True)

    for result in nested_results:
        if isinstance(result, dict) and result is not None:
            data_dictionary.update(result)
        elif isinstance(result, asyncio.TimeoutError):
            print(f"A nested crawl task timed out. Skipping this URL.")
        elif isinstance(result, Exception):
            print(f"An exception occurred during nested crawl: {result}")
    
    if has_text and has_links:
        data_dictionary["input_text_parts"] = input_text_as_sentence

    if not data_dictionary:
        return {"status": "success", "message": "No content was scraped.", "data": {}}
    
    # Format the data for JSON response
    final_data = {}
    for url, data in data_dictionary.items():
        if isinstance(data, tuple) and len(data) == 2:
            content, user_agent = data
            final_data[url] = {"content": content, "user_agent": user_agent}
        else:
            final_data[url] = {"content": data, "user_agent": "N/A"}

    return {"status": "success", "data": final_data}