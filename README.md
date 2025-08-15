# SSI-project (Scraper)

## Key Features:

- Can take multiple URLs as input (separated by space between each link), a simple text/query or a mix of text and links.
- Searches user input text on google and retrieves its search result (default results to retrieve are 2, but can be increased to double digits).
- Can crawl multiple URLs asynchronously & crawls all nested links at level 1 depth (can be configured to crawl even deeper).
- Uses `AsyncWebCrawler` (based on Playwright) for crawling dynamic websites (Javascript enabled), timeout limit can be increased for slower connections/websites.
- Spoofs User Agent for each crawl instance via `fake_useragent` library.
- Added filters to stop the script from crawling user-defined domains, directories & pages.
- Uses `URLExtract` library for identifying & extracting links from user input reliably.

## Backend

Fully integrated with FastAPI Backend. Currently configured to accept input via POST requests (which triggers the scraper) in the following JSON format:

```
{
  "query": "enter text, links or a combination of text and links!"
}
```

### NOTE: 

1) When running the script with Uvicorn, make sure that you do not run the Uvicorn command with the `--reload` flag. This causes a `NotImplementedError` and the script will crash when you send a POST request to it. 
This happens due to `--reload` flag uses a different subprocess management method that conflicts with Playwright's own process handling on the Windows event loop. Thus Asyncio will fail to initiate a Playwright instance, which in turn will crash the script.

The solution is to **remove the `--reload` flag** when running the application, and instead, manage the code reloading manually during development. Example:

```
uvicorn scraper:app
```

2) In order to ensure compatibility, it is highly recommended to run this script with the latest STABLE version of Python. This was developed with Python 3.11.

