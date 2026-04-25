"""
Integration tests for job search workflow
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.models.user import User
from app.models.job import Job
from app.models.saved_job import SavedJob


@pytest.mark.asyncio
class TestJobSearchWorkflow:
    """Test complete job search workflow"""

    async def test_search_and_save_job_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db: AsyncSession
    ):
        """Test searching for jobs and saving them"""
        # Search for jobs
        response = await client.get(
            "/jobs/search?query=developer&location=remote",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)
        
        if jobs:
            job_id = jobs[0]['id']
            
            # Save the job
            save_response = await client.post(
                "/saved-jobs",
                json={"job_id": job_id},
                headers=auth_headers
            )
            
            assert save_response.status_code == 201
            saved_job = save_response.json()
            assert saved_job['job_id'] == job_id

    async def test_get_saved_jobs_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db: AsyncSession
    ):
        """Test retrieving saved jobs"""
        response = await client.get(
            "/saved-jobs",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        saved_jobs = response.json()
        assert isinstance(saved_jobs, list)

    async def test_unsave_job_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db: AsyncSession
    ):
        """Test removing a saved job"""
        # First save a job
        search_response = await client.get(
            "/jobs/search?query=developer",
            headers=auth_headers
        )
        
        if search_response.status_code == 200:
            jobs = search_response.json()
            if jobs:
                job_id = jobs[0]['id']
                
                # Save the job
                save_response = await client.post(
                    "/saved-jobs",
                    json={"job_id": job_id},
                    headers=auth_headers
                )
                
                if save_response.status_code == 201:
                    saved_job = save_response.json()
                    saved_job_id = saved_job['id']
                    
                    # Unsave the job
                    delete_response = await client.delete(
                        f"/saved-jobs/{saved_job_id}",
                        headers=auth_headers
                    )
                    
                    assert delete_response.status_code == 204

    async def test_search_with_filters_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test searching with various filters"""
        filters = {
            "query": "python",
            "location": "remote",
            "salary_min": 100000,
            "experience_level": "senior"
        }
        
        response = await client.get(
            "/jobs/search",
            params=filters,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)

    async def test_job_details_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test getting job details"""
        # First search for jobs
        search_response = await client.get(
            "/jobs/search?query=developer",
            headers=auth_headers
        )
        
        if search_response.status_code == 200:
            jobs = search_response.json()
            if jobs:
                job_id = jobs[0]['id']
                
                # Get job details
                details_response = await client.get(
                    f"/jobs/{job_id}",
                    headers=auth_headers
                )
                
                assert details_response.status_code == 200
                job = details_response.json()
                assert job['id'] == job_id
