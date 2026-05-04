
import asyncio
import sys
import os

# Add Backend to sys.path so we can import app
sys.path.append(os.path.join(os.getcwd(), 'Backend'))

from app.infrastructure.scrapers.jobspy_scraper_impl import JobSpyLibraryScraper

async def test_scraping():
    print("Initializing JobSpyLibraryScraper...")
    scraper = JobSpyLibraryScraper()
    
    query = "Software Engineer"
    location = "San Francisco, CA"
    
    print(f"Scraping jobs for '{query}' in '{location}'...")
    # We only test Indeed for speed and because it's usually reliable
    jobs = await scraper.scrape_jobs(
        query=query, 
        location=location, 
        site_name=["indeed"], 
        max_results=2
    )
    
    print(f"Scraped {len(jobs)} jobs.")
    
    for i, job in enumerate(jobs):
        print(f"\nJob {i+1}:")
        print(f"  Title: {job['title']}")
        print(f"  Company: {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  Source: {job['source']}")
        print(f"  URL: {job['source_url'][:50]}...")

if __name__ == "__main__":
    try:
        asyncio.run(test_scraping())
    except Exception as e:
        print(f"VERIFICATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
