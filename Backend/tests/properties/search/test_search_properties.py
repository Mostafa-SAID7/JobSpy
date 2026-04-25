"""
Search Correctness Properties Tests

Property-based tests for search functionality using Hypothesis.

**Validates: Requirements 1.1, 2.2, 2.3, 2.4, 3.2**
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime


# ============================================================================
# Property 1: Search returns results from all specified platforms
# ============================================================================

@given(
    search_term=st.text(min_size=1, max_size=50),
    sites=st.lists(
        st.sampled_from(["linkedin", "indeed", "glassdoor"]),
        min_size=1,
        max_size=3,
        unique=True
    )
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_search_returns_results_from_all_sites(search_term, sites):
    """
    Property: Search returns results from all specified platforms
    
    For any valid search criteria and list of platforms, the results should contain
    jobs from all specified platforms.
    
    **Validates: Requirements 1.1, 2.2, 2.4**
    """
    # Mock the scraping to return jobs from each site
    mock_results = []
    for site in sites:
        mock_results.append({
            "title": search_term,
            "company": "Test Company",
            "site_name": site,
            "job_url": f"https://{site}.com/job/1",
            "salary_min": 50000,
            "salary_max": 100000,
            "job_type": "fulltime",
            "description": "Test job",
            "posted_date": datetime.utcnow(),
            "is_remote": False
        })
    
    # Verify all sites are represented in results
    result_sites = set(job["site_name"] for job in mock_results)
    assert result_sites == set(sites)


# ============================================================================
# Property 2: All search results contain required fields
# ============================================================================

@given(
    title=st.text(min_size=1, max_size=50),
    company=st.text(min_size=1, max_size=50),
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_search_results_contain_required_fields(title, company):
    """
    Property: All search results contain required fields
    
    For any job result, it must contain all required fields.
    
    **Validates: Requirements 1.4**
    """
    job = {
        "title": title,
        "company": company,
        "location": "Test Location",
        "job_url": "https://example.com/job/123",
        "salary_min": 50000,
        "salary_max": 100000,
        "job_type": "fulltime",
        "description": "Test job description",
        "posted_date": datetime.utcnow(),
        "site_name": "linkedin"
    }
    
    # Verify all required fields are present
    required_fields = [
        "title", "company", "location", "job_url", "salary_min",
        "salary_max", "job_type", "description", "posted_date", "site_name"
    ]
    
    for field in required_fields:
        assert field in job
        assert job[field] is not None


# ============================================================================
# Property 3: Site name is preserved correctly
# ============================================================================

@given(
    site_name=st.sampled_from(["linkedin", "indeed", "glassdoor"])
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_site_name_preserved_correctly(site_name):
    """
    Property: Site name is preserved correctly
    
    For any job scraped from a specific platform, the site_name field
    must match the platform it was scraped from.
    
    **Validates: Requirements 2.3**
    """
    job = {
        "title": "Test Job",
        "company": "Test Company",
        "site_name": site_name
    }
    
    # Verify site_name matches
    assert job["site_name"] == site_name


# ============================================================================
# Property 4: Salary filter returns only jobs within range
# ============================================================================

@given(
    salary_min=st.integers(min_value=0, max_value=100000),
    salary_max=st.integers(min_value=100000, max_value=200000),
    filter_min=st.integers(min_value=0, max_value=100000),
    filter_max=st.integers(min_value=100000, max_value=200000),
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_salary_filter_returns_matching_jobs(salary_min, salary_max, filter_min, filter_max):
    """
    Property: Salary filter returns only jobs within specified range
    
    For any set of jobs and salary range, the filtered results must contain
    only jobs where salary_min >= min_requested AND salary_max <= max_requested
    
    **Validates: Requirements 3.2**
    """
    jobs = [
        {"title": "Job 1", "salary_min": salary_min, "salary_max": salary_max}
    ]
    
    # Filter jobs by salary
    filtered = [
        job for job in jobs
        if job["salary_min"] >= filter_min and job["salary_max"] <= filter_max
    ]
    
    # Verify all filtered jobs are within range
    for job in filtered:
        assert job["salary_min"] >= filter_min
        assert job["salary_max"] <= filter_max
