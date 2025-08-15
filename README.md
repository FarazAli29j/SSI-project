# SSI-project (Scraper)

## Key Features:

- Can take multiple URLs as input (separated by space between each link), a simple text/query or a mix of text and links.
- Searches user input text on google and retrieves its search result (default is 2, but can be increased to double digits).
- Can crawl multiple URLs asynchronously and crawls all nested links at level 1 depth (can be configured to crawl even further).
- Uses "AsyncWebCrawler" (based on Playwright) for crawling dynamic websites (Javascript enabled), timeout limit can be increased for slower connections/websites.
- Spoofs User Agent for each crawl instance
- Added filters to stop the script from crawling user-defined domains, directories & pages.
- Uses "URLExtract" library for identifying & extracting links from user input reliably.

### Fully integrated with FastAPI Backend. Currently configured to accept input via POST requests (which triggers the scraper) in the following JSON format:

```
{
  "query": "enter text, links or a combination of text and links!"
}
```
