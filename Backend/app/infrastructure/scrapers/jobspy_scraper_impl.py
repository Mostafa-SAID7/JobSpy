"""
JobSpy Library Scraper Implementation

This scraper uses the python-jobspy library to aggregate jobs from multiple 
sources including LinkedIn, Indeed, Glassdoor, ZipRecruiter, and Google.
"""

import asyncio
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from jobspy import scrape_jobs

from app.domain.interfaces.scraper_interface import IJobScraper, ScraperConfig

class JobSpyLibraryScraper(IJobScraper):
    """
    Implementation of IJobScraper using the python-jobspy library.
    """
    
    @property
    def source_name(self) -> str:
        """Name of the job source"""
        return "JobSpy Engine"
    
    async def scrape_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Scrape jobs from multiple sources using python-jobspy.
        
        This method wraps the synchronous scrape_jobs function in an 
        async-friendly thread executor.
        """
        
        # Merge default config with kwargs
        config = {
            "site_name": kwargs.get("site_name", ["indeed", "linkedin", "zip_recruiter", "glassdoor", "google", "bayt", "naukri", "bdjobs"]),
            "search_term": query,
            "location": location,
            "results_wanted": kwargs.get("max_results", 50),
            "distance": kwargs.get("distance", 50),
            "job_type": kwargs.get("job_type"),
            "is_remote": kwargs.get("is_remote", False),
            "easy_apply": kwargs.get("easy_apply"),
            "hours_old": kwargs.get("hours_old"),
            "country_indeed": kwargs.get("country_indeed", "USA"),
            "enforce_annual_salary": kwargs.get("enforce_annual_salary", False),
            "proxies": kwargs.get("proxies"),
            "linkedin_fetch_description": kwargs.get("linkedin_fetch_description", True)
        }
        
        # Remove None values to use library defaults
        config = {k: v for k, v in config.items() if v is not None}
        
        try:
            # Run the synchronous scraping in a separate thread to avoid blocking the event loop
            jobs_df = await asyncio.to_thread(scrape_jobs, **config)
            
            if jobs_df is None or jobs_df.empty:
                return []
            
            # Convert DataFrame to list of dictionaries
            return self._map_to_internal_format(jobs_df)
            
        except Exception as e:
            # In a real app, log this properly
            print(f"Error during JobSpy scraping: {str(e)}")
            return []
            
    def _map_to_internal_format(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Maps the JobSpy DataFrame columns to our internal raw job dictionary format.
        """
        jobs = []
        for _, row in df.iterrows():
            job = {
                "source": str(row.get("site", "JobSpy")),
                "title": str(row.get("title", "No Title")),
                "company": str(row.get("company", "Unknown Company")),
                "location": f"{row.get('city', '')}, {row.get('state', '')}, {row.get('country', '')}".strip(", "),
                "description": str(row.get("description", "")) if pd.notna(row.get("description")) else "",
                "source_url": str(row.get("job_url", "")),
                "job_type": str(row.get("job_type", "")) if pd.notna(row.get("job_type")) else None,
                "salary": {
                    "min_amount": float(row.get("min_amount")) if pd.notna(row.get("min_amount")) else None,
                    "max_amount": float(row.get("max_amount")) if pd.notna(row.get("max_amount")) else None,
                    "currency": str(row.get("currency", "USD")) if pd.notna(row.get("currency")) else "USD",
                    "interval": str(row.get("interval", "yearly")) if pd.notna(row.get("interval")) else "yearly"
                },
                "posted_date": row.get("date_posted"),
                "company_logo_url": str(row.get("company_logo", "")) if pd.notna(row.get("company_logo")) else None,
                "source_job_id": str(row.get("id", "")) if pd.notna(row.get("id")) else None,
                # Site specific fields
                "experience_range": str(row.get("experience_range", "")) if pd.notna(row.get("experience_range")) else None,
                "vacancy_count": int(row.get("vacancy_count")) if pd.notna(row.get("vacancy_count")) else None,
                "company_rating": float(row.get("company_rating")) if pd.notna(row.get("company_rating")) else None,
                "job_level": str(row.get("job_level", "")) if pd.notna(row.get("job_level")) else None,
            }
            
            # If posted_date is a string or timestamp, ensure it's ISO format or datetime
            if pd.isna(job["posted_date"]):
                job["posted_date"] = datetime.utcnow().isoformat()
            elif hasattr(job["posted_date"], "isoformat"):
                job["posted_date"] = job["posted_date"].isoformat()
                
            jobs.append(job)
            
        return jobs

    async def health_check(self) -> bool:
        """Basic check - we assume library is operational if it can be imported"""
        return True
    
    async def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        JobSpy currently focuses on search. Detailed fetching is usually part of 
        the search with linkedin_fetch_description=True.
        """
        # For now, we return None and rely on the initial scrape
        return None
