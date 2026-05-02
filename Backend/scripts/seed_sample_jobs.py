"""
Sample Job Data Seeder (Refactored to Clean Architecture)

Creates sample job data for testing the JobSpy application.
Now uses Clean Architecture with use cases and dependency injection.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the Backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import Base

# Clean Architecture imports
from app.infrastructure.persistence.sqlalchemy.repositories.job_repository_impl import JobRepositoryImpl
from app.domain.services.job_scoring_service import JobScoringService
from app.domain.services.skill_extraction_service import SkillExtractionService
from app.application.mappers.job_mapper import JobMapper
from app.application.use_cases.scraping.process_scraped_jobs_use_case import ProcessScrapedJobsUseCase

# Sample job data
SAMPLE_JOBS = [
    {
        "title": "Frontend Developer",
        "company": "TechCorp Inc",
        "location": "San Francisco, CA",
        "salary_min": 80000,
        "salary_max": 120000,
        "salary_currency": "USD",
        "job_type": "Full-time",
        "description": "We are looking for a skilled Frontend Developer to join our team. You will be responsible for building user interfaces using React, Vue.js, and modern JavaScript frameworks. Experience with TypeScript, CSS3, and responsive design is required.",
        "requirements": [
            "3+ years of experience with React or Vue.js",
            "Strong knowledge of JavaScript/TypeScript",
            "Experience with CSS3 and responsive design",
            "Familiarity with Git and version control",
            "Bachelor's degree in Computer Science or related field"
        ],
        "benefits": ["Health insurance", "401k matching", "Remote work options", "Professional development budget"],
        "source_url": "https://example.com/jobs/frontend-dev-1",
        "source_job_id": "FE001",
        "posted_date": datetime.utcnow() - timedelta(days=2),
        "deadline": datetime.utcnow() + timedelta(days=28),
        "company_logo_url": "https://example.com/logos/techcorp.png",
        "company_website": "https://techcorp.com",
        "experience_level": "Mid Level",
        "is_remote": 2  # Hybrid
    },
    {
        "title": "Backend Python Developer",
        "company": "DataFlow Solutions",
        "location": "New York, NY",
        "salary_min": 90000,
        "salary_max": 140000,
        "salary_currency": "USD",
        "job_type": "Full-time",
        "description": "Join our backend team to build scalable APIs and microservices using Python, FastAPI, and PostgreSQL. You'll work on high-performance systems that process millions of requests daily.",
        "requirements": [
            "5+ years of Python development experience",
            "Experience with FastAPI, Django, or Flask",
            "Strong knowledge of SQL and PostgreSQL",
            "Experience with Docker and Kubernetes",
            "Understanding of microservices architecture"
        ],
        "benefits": ["Competitive salary", "Stock options", "Health insurance", "Flexible hours"],
        "source_url": "https://example.com/jobs/backend-python-1",
        "source_job_id": "BE001",
        "posted_date": datetime.utcnow() - timedelta(days=1),
        "deadline": datetime.utcnow() + timedelta(days=30),
        "company_logo_url": "https://example.com/logos/dataflow.png",
        "company_website": "https://dataflow.com",
        "experience_level": "Senior Level",
        "is_remote": 1  # Remote
    },
    {
        "title": "Full Stack JavaScript Developer",
        "company": "StartupXYZ",
        "location": "Austin, TX",
        "salary_min": 70000,
        "salary_max": 100000,
        "salary_currency": "USD",
        "job_type": "Full-time",
        "description": "We're a fast-growing startup looking for a Full Stack Developer proficient in Node.js, React, and MongoDB. You'll have the opportunity to work on cutting-edge projects and shape our technology stack.",
        "requirements": [
            "3+ years of JavaScript development",
            "Experience with Node.js and Express",
            "Proficiency in React and modern frontend tools",
            "Knowledge of MongoDB or other NoSQL databases",
            "Experience with AWS or cloud platforms"
        ],
        "benefits": ["Equity package", "Health insurance", "Unlimited PTO", "Learning budget"],
        "source_url": "https://example.com/jobs/fullstack-js-1",
        "source_job_id": "FS001",
        "posted_date": datetime.utcnow() - timedelta(hours=12),
        "deadline": datetime.utcnow() + timedelta(days=21),
        "company_logo_url": "https://example.com/logos/startupxyz.png",
        "company_website": "https://startupxyz.com",
        "experience_level": "Mid Level",
        "is_remote": 0  # On-site
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudTech Systems",
        "location": "Seattle, WA",
        "salary_min": 100000,
        "salary_max": 150000,
        "salary_currency": "USD",
        "job_type": "Full-time",
        "description": "Looking for a DevOps Engineer to manage our cloud infrastructure and CI/CD pipelines. Experience with AWS, Docker, Kubernetes, and Infrastructure as Code is essential.",
        "requirements": [
            "4+ years of DevOps experience",
            "Strong knowledge of AWS services",
            "Experience with Docker and Kubernetes",
            "Proficiency in Terraform or CloudFormation",
            "Experience with CI/CD tools (Jenkins, GitLab CI)"
        ],
        "benefits": ["High salary", "Stock options", "Remote work", "Conference budget"],
        "source_url": "https://example.com/jobs/devops-1",
        "source_job_id": "DO001",
        "posted_date": datetime.utcnow() - timedelta(days=3),
        "deadline": datetime.utcnow() + timedelta(days=25),
        "company_logo_url": "https://example.com/logos/cloudtech.png",
        "company_website": "https://cloudtech.com",
        "experience_level": "Senior Level",
        "is_remote": 1  # Remote
    },
    {
        "title": "Junior Web Developer",
        "company": "WebDesign Pro",
        "location": "Los Angeles, CA",
        "salary_min": 50000,
        "salary_max": 70000,
        "salary_currency": "USD",
        "job_type": "Full-time",
        "description": "Entry-level position for a Junior Web Developer. Perfect for recent graduates or career changers. You'll work with HTML, CSS, JavaScript, and learn modern frameworks on the job.",
        "requirements": [
            "Basic knowledge of HTML, CSS, JavaScript",
            "Familiarity with responsive design",
            "Understanding of version control (Git)",
            "Bachelor's degree or coding bootcamp certificate",
            "Eagerness to learn and grow"
        ],
        "benefits": ["Mentorship program", "Health insurance", "Paid training", "Career growth"],
        "source_url": "https://example.com/jobs/junior-web-1",
        "source_job_id": "JW001",
        "posted_date": datetime.utcnow() - timedelta(hours=6),
        "deadline": datetime.utcnow() + timedelta(days=14),
        "company_logo_url": "https://example.com/logos/webdesignpro.png",
        "company_website": "https://webdesignpro.com",
        "experience_level": "Entry Level",
        "is_remote": 2  # Hybrid
    },
    {
        "title": "Data Scientist",
        "company": "AI Innovations",
        "location": "Boston, MA",
        "salary_min": 110000,
        "salary_max": 160000,
        "salary_currency": "USD",
        "job_type": "Full-time",
        "description": "Join our AI team to build machine learning models and analyze large datasets. Experience with Python, TensorFlow, and statistical analysis is required.",
        "requirements": [
            "PhD or Master's in Data Science, Statistics, or related field",
            "5+ years of experience with Python and R",
            "Experience with TensorFlow, PyTorch, or scikit-learn",
            "Strong statistical analysis skills",
            "Experience with big data tools (Spark, Hadoop)"
        ],
        "benefits": ["Research budget", "Conference attendance", "Stock options", "Flexible schedule"],
        "source_url": "https://example.com/jobs/data-scientist-1",
        "source_job_id": "DS001",
        "posted_date": datetime.utcnow() - timedelta(days=4),
        "deadline": datetime.utcnow() + timedelta(days=35),
        "company_logo_url": "https://example.com/logos/aiinnovations.png",
        "company_website": "https://aiinnovations.com",
        "experience_level": "Senior Level",
        "is_remote": 1  # Remote
    },
    {
        "title": "Mobile App Developer (React Native)",
        "company": "MobileFirst Inc",
        "location": "Chicago, IL",
        "salary_min": 85000,
        "salary_max": 125000,
        "salary_currency": "USD",
        "job_type": "Full-time",
        "description": "Develop cross-platform mobile applications using React Native. You'll work on both iOS and Android apps for our growing user base.",
        "requirements": [
            "3+ years of React Native development",
            "Experience with iOS and Android development",
            "Knowledge of JavaScript/TypeScript",
            "Familiarity with mobile app deployment",
            "Understanding of mobile UI/UX principles"
        ],
        "benefits": ["Device allowance", "Health insurance", "Gym membership", "Team outings"],
        "source_url": "https://example.com/jobs/mobile-dev-1",
        "source_job_id": "MD001",
        "posted_date": datetime.utcnow() - timedelta(days=1),
        "deadline": datetime.utcnow() + timedelta(days=20),
        "company_logo_url": "https://example.com/logos/mobilefirst.png",
        "company_website": "https://mobilefirst.com",
        "experience_level": "Mid Level",
        "is_remote": 2  # Hybrid
    },
    {
        "title": "UI/UX Designer",
        "company": "DesignStudio Creative",
        "location": "Portland, OR",
        "salary_min": 65000,
        "salary_max": 95000,
        "salary_currency": "USD",
        "job_type": "Full-time",
        "description": "Create beautiful and intuitive user interfaces for web and mobile applications. Experience with Figma, Adobe Creative Suite, and user research is preferred.",
        "requirements": [
            "3+ years of UI/UX design experience",
            "Proficiency in Figma and Adobe Creative Suite",
            "Understanding of user-centered design principles",
            "Experience with prototyping and wireframing",
            "Portfolio demonstrating design skills"
        ],
        "benefits": ["Creative freedom", "Design software licenses", "Health insurance", "Work from home"],
        "source_url": "https://example.com/jobs/uiux-designer-1",
        "source_job_id": "UX001",
        "posted_date": datetime.utcnow() - timedelta(hours=18),
        "deadline": datetime.utcnow() + timedelta(days=18),
        "company_logo_url": "https://example.com/logos/designstudio.png",
        "company_website": "https://designstudio.com",
        "experience_level": "Mid Level",
        "is_remote": 1  # Remote
    }
]


async def seed_jobs():
    """
    Seed the database with sample job data.
    
    REFACTORED: Now uses Clean Architecture with use cases.
    """
    print("🌱 Starting job data seeding (Clean Architecture)...")
    
    # Create database engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
    )
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        # Initialize dependencies (Clean Architecture)
        job_repository = JobRepositoryImpl(session)
        scoring_service = JobScoringService()
        skill_service = SkillExtractionService()
        job_mapper = JobMapper()
        
        # Create use case
        process_jobs_use_case = ProcessScrapedJobsUseCase(
            job_repository=job_repository,
            scoring_service=scoring_service,
            skill_service=skill_service,
            job_mapper=job_mapper,
        )
        
        print(f"📝 Processing {len(SAMPLE_JOBS)} sample jobs...")
        
        # Process jobs using the use case
        result = await process_jobs_use_case.execute(
            SAMPLE_JOBS, 
            source="SampleData"
        )
        
        # Commit the transaction
        await session.commit()
        
        print(f"✅ Seeding completed!")
        print(f"   - Saved: {result['saved']} jobs")
        print(f"   - Duplicates: {result['duplicates']} jobs")
        print(f"   - Errors: {result['errors']} jobs")
        print(f"   - Total processed: {result['total_processed']} jobs")
        
        if result['errors'] > 0:
            print("⚠️  Some jobs had errors during processing")
        
        return result


async def main():
    """Main function to run the seeding process."""
    try:
        result = await seed_jobs()
        
        if result['saved'] > 0:
            print(f"\n🎉 Successfully seeded {result['saved']} jobs!")
            print("You can now search for jobs in the JobSpy application.")
            print("\nSample searches to try:")
            print("- 'Frontend Developer'")
            print("- 'Python'")
            print("- 'Remote'")
            print("- 'JavaScript'")
        else:
            print("\n❌ No jobs were saved. Check the logs for errors.")
            
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
